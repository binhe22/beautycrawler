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

geventThread = []

class flyer():
    id = 0
    channels = {}
    redisIp = ""
    redisPort = 0
    redisPassword = ""
    def __init__(self, redisIp=config["redisIp"], redisPort=config["redisPort"], redisPassword=config["redisPassword"], redisDb=config["redisDb"] ):
        """get redis instance and check if it can be used"""
        self.redisIp = redisIp
        self.redisPort = redisPort
        self.redisPassword = redisPassword
        self.redisDb = redisDb
        r = self.getRedis()
        if r.ping():
            ps = r.pubsub()
            ps.subscribe("rootChannel")  #订阅两个频道，分别是count_alarm ip_alarm
            self.channels["rootChannel"] = ps
            print "init ok"

    def getRedis(self):
        pool = redis.ConnectionPool(host=self.redisIp, port=self.redisPort, password=self.redisPassword, db=self.redisDb)
        return redis.Redis(connection_pool=pool)

    def getPubsub(self):
        r = self.getRedis()
        return r.pubsub()

    def start(self):
        """get the process id in the cluster"""
        r = self.getRedis()
        self.id = r.incr("flyerId")
        return self.id

    def stop(self):
        """send to all process to exit"""
        r = self.getRedis()
        r.set("flyerStop", 1)
        exit(0)

    def send(self, channelName, message):
        """send message to chanel (if you want sent to specific process you can use
        difference chanel name in different process)"""
        r = self.getRedis()
        return r.publish(channelName, message)

    def recieve(self, channelName):
        """recieve num messages from chanel"""
        ps = self.getPubsub()
        ps.subscribe(channelName)
        for item in ps.listen():
            if item['type'] == 'message':
                    return item["data"]

    def sendAll(self, message):
        """send message to each process"""
        r = self.getRedis()
        r.publish("rootChannel", message)

    def recieveAll(self):
        """recieve message from all"""
        ps = self.channels["rootChannel"]
        for item in ps.listen():
            if item['type'] == 'message':
                    return item["data"]
    def clean(self):
        r = self.getRedis()
        r.flushdb()

def runProcess(cmd):
    child=pexpect.spawn(cmd)
    print child.read()
    child.close()
    return 1


def stop():
    pass

def sshRun(hostFile, remotePath, localFile):
    f = open(hostFile)
    hostList = []
    for i in f.readlines():
        hostList.append(i)
    f.close()
    cmdList = []
    for i in xrange(len(hostList)):
        cmd='ssh %s "python %s >%slog%d"'%(hostList[i],remotePath+"/"+localFile, remotePath+"/",i)
        cmdList.append(cmd)
    gevent.joinall([ gevent.spawn(runProcess, cmd) for cmd in cmdList]+[gevent.spawn(stop)])
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





