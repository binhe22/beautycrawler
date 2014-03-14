#!/usr/bin/env python
#coding=utf-8
import gevent
from gevent import monkey;monkey.patch_all();
import argparse
import redis
from scpfile import scp
import pexpect
import time
from redisconfig import config
from crawler import crawl
from flyer import flyer

class beautyCrawler(crawl):
    def display(self):
        while 1:
            try:
                r = self.getRedis()
                if r.get("programExit") == 1:
                    print "go to exit"
                    return
                print "------------------------------------------"
                print "saved img:", r.scard("saved")
                print "saving img(to crawl)", r.scard("saving")
                print "crawledurl", r.scard("crawled")
                print "crawlingurl", r.scard("crawling")
                print "saveErrorUrl", r.scard("saveerror")
                print "crawlErrorUrl", r.scard("cralwerror")
                print "------------------------------------------"
            except KeyboardInterrupt:
                r = self.getRedis()
                r.set("programExit", 1)
                return
            gevent.sleep(5)

def runProcess(cmd):
    child=pexpect.spawn(cmd)
    print child.read()
    child.close()
    return 1

def sshRun(hostFile, remotePath, localFile):
    f = open(hostFile)
    hostList = []
    for i in f.readlines():
        hostList.append(i)
    f.close()
    cmdList = []
    for i in xrange(len(hostList)):
        cmd='ssh %s "nohup python %s >%slog%d&"'%(hostList[i],remotePath+"/"+localFile, remotePath+"/",i)
        cmdList.append(cmd)
    gevent.joinall([ gevent.spawn(runProcess, cmd) for cmd in cmdList])
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Flyer--An easy MPI-like distributed\
            tool for python, to ran applications in clusters.')
    parser.add_argument('--h', action="store", default="host.list", dest="hostList")
    parser.add_argument('--f', action="store", default="file.list", dest="fileList")
    parser.add_argument('--r', action="store", default="/tmp", dest="rpath")
    parser.add_argument('--e', action="store", default="run.py", dest="exeFile")
    results = parser.parse_args()
    print results.exeFile
    flyerTest = flyer()
    flyerTest.clean()
    print flyerTest.start()
    scpInfo = scp(results.hostList, results.rpath, results.fileList)
    sshRun(results.hostList, results.rpath, results.exeFile)
    beauty = beautyCrawler()
    beauty.display()





