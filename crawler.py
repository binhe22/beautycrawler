#!/usr/bin/env python2.7
#!coding:utf8
import gevent
from gevent import monkey; monkey.patch_all();
import requests
import re
from BeautifulSoup import BeautifulSoup
import redis
import os


headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip,deflate,sdch',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Connection':'keep-alive',
        'Host':'www.22mm.cc',
        'Referer':'http://www.22mm.cc/mm/suren/PiaHaimeHmHPaHJHC.html',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'
        }

config = {"redisIp":"127.0.0.1",
        "redisPort":6379,
        "redisDb":0,
        "redisPassword":'',
        "host":["22mm.cc","meimei22.com"]
        }

proxies = {
        "http":"http://183.207.228.2:81"
        }

chunk_size = 256
poolSize = 1

def getRedis():
    r=redis.StrictRedis(host=config["redisIp"], port=config["redisPort"],db=config["redisDb"] )
    if r == None:
        print "connect error"
        exit()
    return r

def getUrl(Tags, host, type):
    urls = []
    for tag in Tags:
            url = tag[type]
            print url
            flag = 0
            for i in config["host"]:
                if i in url:
                    flag = 1
                    break
            if not flag and "http://" in url:
                continue

            if url.startswith("http://"):
                pass
            elif url.startswith("/"):
                url = host + url[1:]
            else:
                url = host+url
            urls.append(url)
    print urls
    return urls


def goNext(argIn):
    rq = requests.get(argIn, proxies=proxies, headers=headers, timeout=10)
    host = re.findall("^(http:\/\/.*\.[a-z]*\/)", rq.url)
    try:
        host = host[0]
    except IndexError:
        print "get host error"
        return 0
    if rq.status_code != 200:
        return 0
    htmlContent = rq.text.encode(rq.encoding).decode("utf8")
    soup = BeautifulSoup(htmlContent)
    aTags = soup.findAll('a', href=True)
    urls = getUrl(aTags, host, "href")
    #ifMatchDeep =  re.match("\/[a-zA-Z]*\/[a-zA-Z]*\/[a-zA-Z\.]*", href)
    r = getRedis()
    for url in urls:
        if not r.sismember("crawled", url):
            r.sadd("crawling",url)
            print "gonext", url
    #saveUrls = getUrl(soup.findAll('img', src=True), host, "src")
    r.srem("crawling", argIn)
    r.sadd("crawled", argIn)

    saveUrls = []
    try:
        saveUrl = re.findall('arrayImg\[[0-9]*\]="(.*\.jpg)";', rq.text)
        print saveUrl
        saveUrl = saveUrl[0]
        saveUrl = saveUrl.replace("big","pic")
    except IndexError:
        return 1

    saveUrls.append(saveUrl)
    for url in saveUrls:
        if not r.sismember("saved", url):
            r.sadd("saving", url)
            print "gosaving", url
    return 1

def goSave():
    r = getRedis()
    url = r.srandmember("saving")
    if not url:
        return 0
    print "connect",url
    rq = requests.get(url, headers=headers, proxies=proxies, timeout=10, stream=True)
    if rq.status_code != 200:
        print "save connect error:", url
        return 0
    fileName = re.findall("\.com\/(.*\.jpg)$", url)[0]
    mkdir(fileName)
    with open(fileName, 'wb+') as fd:
        for chunk in rq.iter_content(chunk_size):
            fd.write(chunk)
    fd.close()
    r.sadd("saved", url)
    r.srem("saving", url)
    return 1

def mkdir(path):
     tmp = path.split("/")
     tmp = "/".join(tmp[:-1])
     if not os.path.exists(tmp):
         os.makedirs(tmp)


def saveForever():
    while 1:
        try:
            goSave()
        except Exception, e:
            print "error",e
            gevent.sleep(1)

def crawlForever():
    while 1:
        try:
            r=getRedis()
            url = r.srandmember("crawling")
            if not url:
                gevent.sleep(1)
                continue
            goNext(url)
        except Exception,e:
            print "error",e
            gevent.sleep(1)



def main():
    r = getRedis()
    r.sadd("crawling", "http://www.22mm.cc/mm/qingliang/")
    r.sadd("crawling", "http://www.22mm.cc/mm/jingyan/")
    r.sadd("crawling", "http://www.22mm.cc/mm/bagua/")
    r.sadd("crawling", "http://www.22mm.cddc/mm/suren/")
    gevent.joinall([gevent.spawn(saveForever) for i in range(10)]+[gevent.spawn(crawlForever) for i in range(10)])

if __name__ == '__main__':
    main()
