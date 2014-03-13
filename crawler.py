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
import config



class crawl(object):
    headers = config.headers
    config = config.config
    chunk_size = config["chunk_size"]
    proxiesNum = config["proxiesNum"]
    proxies = proxy.startRun()[0:proxiesNum]
    crawlNum = config["crawlNum"]
    saveNum =  config["saveNum"]
    crawlErrorHandleNum = config["crawlErrorHandleNum"]
    saveErrorHandleNum = config["saveErrorHandleNum"]
    redisCrawlingKey = config["redisCrawlingKey"]
    redisSavingKey = config["redisSavingKey"]
    redisCrawledKey = config["redisCrawledKey"]
    redisSavedKey = config["redisSavedKey"]
    redisCrawlErrorKey = config["redisCrawlErrorKey"]
    redisSaveErrorKey = config["redisSaveErrorKey"]
    timeout = config["timeout"]
    redisIp = config["redisIp"]
    redisPort = config["redisPort"]
    redisDb = config["redisDb"]
    redisPassword = config["redisPassword"]
    proxyOn = config["proxyOn"]
    programExit = 0
    outDir = config["outDir"]
    saveLimit = config["saveLimit"]

    def getRedis(self):
        pool = redis.ConnectionPool(host=self.redisIp, port=self.redisPort, password=self.redisPassword, db=self.redisDb)
        return redis.Redis(connection_pool=pool)

    def getUrl(self, Tags, host, hosturl, type):
        urls = []
        for tag in Tags:
                url = tag[type]
                flag = 0
                for i in self.config["host"]:
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
        return urls


    def findUrlNext(self, htmlContent, rq, host):
        soup = BeautifulSoup(htmlContent)
        aTags = soup.findAll('a', href=True)
        hostUrl =  "/".join(rq.url.split("/")[0:-1])
        urls = self.getUrl(aTags, host, hostUrl, "href")
        return urls

    def findUrlSave(self, htmlContent, rq, host):
        saveUrls = []
        try:
            saveUrl = re.findall('arrayImg\[[0-9]*\]="(.*\.jpg)";', htmlContent)[0]
            saveUrl = saveUrl.replace("big", "pic")
            saveUrl = saveUrl.replace('"','')
            saveUrl = saveUrl.split(";")
            for i in saveUrl:
                url=re.findall('http:\/\/.*\.jpg', i)[0]
                url.replace("big","pic")
                saveUrls.append(url)
        except IndexError:
            print "findUrlSave IndexError"
            return
        return saveUrls

    def goNext(self, argIn):
        if self.proxyOn:
            rq = requests.get(argIn, headers=self.headers, proxies={"http":self.proxies[random.randint(0,self.proxiesNum-1)]},timeout=self.timeout)
        else:
            rq = requests.get(argIn, headers=self.headers, timeout=self.timeout)
        r = self.getRedis()
        host = re.findall("^(http:\/\/.*\.[a-z]*\/)", rq.url)
        try:
            host = host[0]
        except IndexError:
            print "get host error"
            return 0
        if rq.status_code != 200:
            print "error",rq.status_code,argIn
            r.srem(self.redisCrawlingKey, argIn)
            r.sadd(self.redisCrawlErrorKey, argIn)
            return 0
        urls = self.findUrlNext(rq.text, rq, host)
        for url in urls:
            if not r.sismember(self.redisCrawledKey, url):
                r.sadd(self.redisCrawlingKey,url)
                print "gonext", url
        r.srem(self.redisCrawlingKey, argIn)
        r.sadd(self.redisCrawledKey, argIn)
        saveUrls = self.findUrlSave(rq.text, rq, host)
        for url in saveUrls:
            if not r.sismember(self.redisSavedKey, url):
                r.sadd(self.redisSavingKey, url)
                print "gosaving", url
        return 1

    def goSave(self, argIn):
        r = self.getRedis()
        url = argIn
        if self.proxyOn:
            rq = requests.get(url, headers=self.headers, proxies={"http":self.proxies[random.randint(0,self.proxiesNum-1)]}, timeout=self.timeout, stream=True)
        else:
            rq = requests.get(url, headers=self.headers, timeout=self.timeout, stream=True)
        if rq.status_code != 200:
            print "save connect error:", url, rq.status_code
            r.srem(self.redisSavingKey, url)
            r.sadd(self.redisSaveErrorKey, url)
            return 0
        fileName = re.findall("\.com\/(.*\.jpg)$", url)[0]
        self.mkdir(fileName)
        with open(fileName, 'wb+') as fd:
            for chunk in rq.iter_content(self.chunk_size):
                fd.write(chunk)
        fd.close()
        r.sadd(self.redisSavedKey, url)
        r.srem(self.redisSavingKey, url)
        return 1


    def mkdir(self, path):
         tmp = path.split("/")
         tmp = "/".join(tmp[:-1])
         tmp = self.outDir + tmp
         tmp = tmp.rstrip()
         print tmp
         if not os.path.exists(tmp):
             os.makedirs(tmp)


    def saveForever(self):
        while 1:
            try:
                r=self.getRedis()
                if r.get("programExit"):
                    return
                url = r.srandmember(self.redisSavingKey)
                if not url:
                    if not r.srandmember(self.redisCrawlingKey):
                        r.set("programExit", 1)
                        return
                    gevent.sleep(1)
                    continue
                self.goSave(url)
            except Exception, e:
                print "saveForever error",e
                gevent.sleep(1)

    def crawlForever(self):
        while 1:
            try:
                r=self.getRedis()
                if r.get("programExit"):
                    return
                url = r.srandmember(self.redisCrawlingKey)
                if not url:
                    if not r.srandmember(self.redisSavingKey):
                        r.set("programExit", 1)
                        return
                    return
                self.goNext(url)
            except Exception,e:
                print "crawlForever error",e
                gevent.sleep(1)
    def saveErrorHandleForever(self):
        while 1:
            try:
                r = self.getRedis()
                if r.get("programExit"):
                    return
                url = r.srandmember(self.redisSaveErrorKey)
                if not url:
                    gevent.sleep(1)
                    continue
                if(self.goSave(url)):
                    r.srem(self.redisSaveErrorKey, url)
            except Exception, e:
                print "errorHandleForever error:", e
                gevent.sleep(1)

    def crawlErrorHandleForever(self):
        while 1:
            try:
                r = self.getRedis()
                if r.get("programExit"):
                    return
                url = r.srandmember(self.redisCrawlErrorKey)
                if not url:
                    gevent.sleep(1)
                    continue
                if(self.goNext(url)):
                    r.srem(self.redisCrawlErrorKey, url)
            except Exception, e:
                print "badUrlHandleForever error:", e
                gevent.sleep(1)
    def printConfig(self):
        print "-----------------config----------------------------"
        print "redisIp", self.redisIp
        print "redisPort", self.redisPort
        print "redisDb", self.redisDb
        print "redisPassword", self.redisPassword
        print "chunk_size", self.chunk_size
        print "proxiesNum", self.proxiesNum
        print "crawlNum", self.crawlNum
        print "saveNum", self.saveNum
        print "crawlErrorHandleNum", self.crawlErrorHandleNum
        print "saveErrorHandleNum", self.saveErrorHandleNum
        print "redisCrawlingKey", self.redisCrawlingKey
        print "redisSavingKey", self.redisSavingKey
        print "redisCrawledKey", self.redisCrawledKey
        print "redisSavedKey", self.redisSavedKey
        print "redisCrawlErrorKey", self.redisCrawlErrorKey
        print "redisSaveErrorKey", self.redisSaveErrorKey
        print "proxyOn", self.proxyOn
        print "proxies:"
        for i in self.proxies:
            print i
        print "-----------------config end----------------------------"

    def otherExit(self):
        while 1:
            r = self.getRedis()
            savedImg = r.scard("saved")
            print "savedImg", savedImg
            if savedImg > self.saveLimit:
                r.set("programExit", 1)
                return
            gevent.sleep(0)

    def run(self):
        self.printConfig()
        gevent.sleep(2)
        r = self.getRedis()
        r.delete("programExit")
        for i in self.config["seed"]:
            r.sadd(self.redisCrawlingKey, i)
        gevent.joinall([gevent.spawn(self.saveForever) for i in range(self.saveNum)]+[gevent.spawn(self.crawlForever) for i in range(self.crawlNum)]
                +[gevent.spawn(self.crawlErrorHandleForever) for i in range(self.crawlErrorHandleNum)]+[gevent.spawn(self.saveErrorHandleForever) for i in range(self.saveErrorHandleNum)]+[gevent.spawn(self.otherExit)])

if __name__ == '__main__':
    crawl = crawl()
    crawl.run()
