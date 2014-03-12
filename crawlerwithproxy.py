#!/usr/bin/env python2.7
#!coding:utf8
import gevent
from gevent import monkey; monkey.patch_all();
import requests
import re
from BeautifulSoup import BeautifulSoup
import redis
import os
import proxy
import random
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

chunk_size = 256
poolSize = 1

proxies = proxy.startRun()[1:20]

def getRedis():
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    return redis.Redis(connection_pool=pool)

def getUrl(Tags, host, hosturl, type):
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
                url = hosturl+"/"+url
            urls.append(url)
    print urls
    return urls


def goNext(argIn):
    rq = requests.get(argIn, headers=headers, proxies={"http":proxies[random.randint(0,18)]},timeout=10)
    r = getRedis()
    host = re.findall("^(http:\/\/.*\.[a-z]*\/)", rq.url)
    try:
        host = host[0]
    except IndexError:
        print "get host error"
        return 0
    if rq.status_code != 200:
        print "error",rq.status_code
        #r.srem("crawling", argIn)
        #r.sadd("badurl", argIn)
        return 0
    #htmlContent = rq.text.encode(rq.encoding).decode("utf8")
    htmlContent = rq.text
    soup = BeautifulSoup(htmlContent)
    aTags = soup.findAll('a', href=True)
    hostUrl =  "/".join(rq.url.split("/")[0:-1])
    urls = getUrl(aTags, host, hostUrl, "href")
    #ifMatchDeep =  re.match("\/[a-zA-Z]*\/[a-zA-Z]*\/[a-zA-Z\.]*", href)
    for url in urls:
        if not r.sismember("crawled", url):
            r.sadd("crawling",url)
            print "gonext", url
    #saveUrls = getUrl(soup.findAll('img', src=True), host, "src")
    r.srem("crawling", argIn)
    r.sadd("crawled", argIn)

    saveUrls = []
    try:
        saveUrl = re.findall('arrayImg\[[0-9]*\]="(.*\.jpg)";', rq.text)[0]
        saveUrl = saveUrl.replace("big", "pic")
        saveUrl = saveUrl.replace('"','')
        saveUrl = saveUrl.split(";")
        for i in saveUrl:
            url=re.findall('http:\/\/.*\.jpg', i)[0]
            url.replace("big","pic")
            saveUrls.append(url)
    except IndexError:
        return 1
    print "saving url",saveUrls

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
    rq = requests.get(url, headers=headers, proxies={"http":proxies[random.randint(0,18)]}, timeout=10, stream=True)
    if rq.status_code != 200:
        print "save connect error:", url
        r.srem("saving", url)
        r.sadd("error", url)
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
            print "save"
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
            print url
            goNext(url)
        except Exception,e:
            print "error",e
            gevent.sleep(1)



def main():
    r = getRedis()
    r.sadd("crawling", "http://www.22mm.cc/mm/qingliang/")
    r.sadd("crawling", "http://www.22mm.cc/mm/jingyan/")
    r.sadd("crawling", "http://www.22mm.cc/mm/bagua/")
    r.sadd("crawling", "http://www.22mm.cc/mm/suren/")
    gevent.joinall([gevent.spawn(saveForever) for i in range(50)]+[gevent.spawn(crawlForever) for i in range(50)])

if __name__ == '__main__':
    main()
