#!/usr/bin/env python2.7
#!coding:utf8

from gevent import monkey; monkey.patch_all();
import requests
import re
from gevent.pool import Pool
from BeautifulSoup import BeautifulSoup
import redis



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
        }

proxies = {
        "http":'http://58.134.102.231:8080'
        }

chunk_size = 256
poolSize = 10
pool = Pool(poolSize)

def getRedis():
    r=redis.StrictRedis(host=config["redisIp"], port=config["redisPort"],db=config["redisDb"] )
    if r == None:
        print "connect error"
        exit()
    return r


def goNext():
    r = getRedis()
    url = r.srandmember("crawling")
    if not url:
        return 0
    rq = requests.get(url, proxies=proxies, headers=headers, timeout=10)
    host = rq.url
    if rq.status_code != 200:
        r.sadd("crawling", url)
        pool.spawn(goNext)
        return 0
    htmlContent = rq.text.encode(rq.encoding).decode("utf8")
    soup = BeautifulSoup(htmlContent)
    for tag in soup.findAll('a', href=True):
            url = tag['href']
            print url
            if url.startswith("http://"):
                pass
            elif url.startswith("/"):
                url = host + url[1:]
            else:
                url = host+url
            #ifMatchDeep =  re.match("\/[a-zA-Z]*\/[a-zA-Z]*\/[a-zA-Z\.]*", href)
            if not r.sismember("crawled", url):
                r.sadd("crawling",url)
                pool.spawn(goNext)
                print "gonext", url
    for tag in soup.findAll('img', src=True):
            url = tag["src"]
            print url
            if not r.sismember("saved", url):
                r.sadd("saving", url)
            pool.spawn(goSave)
            print "gosaving", url
    return 1

def goSave():
    r = getRedis()
    url = r.srandmember("saving")
    if not url:
        return 0
    rq = requests.get(url, proxies=proxies, headers=headers, timeout=10, stream=True)
    if rq.status_code != 200:
        r.sadd("saving", url)
        pool.spawn(goSave)
        return 0
    fileName = re.findall("\.com\/(.*\.jpg)$", url)[0]
    with open(fileName, 'wb') as fd:
        for chunk in rq.iter_content(chunk_size):
            fd.write(chunk)
    r.sadd("saved", url)
    return 1


def goForever():
     pool.spawn(goNext)
     pool.join()

def main():
    r = getRedis()
    r.sadd("crawling", "http://www.22mm.cc/mm/bagua/PiadPabmamaPaaeaJ.html")
    #r.sadd("crawling", "http://www.22mm.cc/mm/qingliang/")
    #r.sadd("crawling", "http://www.22mm.cc/mm/jingyan/")
    #r.sadd("crawling", "http://www.22mm.cc/mm/bagua/")
    #r.sadd("crawling", "http://www.22mm.cddc/mm/suren/")
    goForever()

if __name__ == '__main__':
    main()
