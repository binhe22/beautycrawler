#!/usr/bin/python
import pexpect

def scp(hostFile, remotePath, listFile):
    f = open(hostFile)
    hostList = []
    for i in f.readlines():
        hostList.append(i.rstrip().lstrip())
    f.close()
    exeInfo = []
    f = open(listFile)
    fileList = []
    for i in f.readlines():
        fileList.append(i.rstrip().lstrip())
    f.close()
    fileList = " ".join(fileList)
    for i in hostList:
        print "sending to",i
        cmd='scp -r %s %s:%s'%(fileList,i,remotePath)
        child=pexpect.spawn(cmd)
        exeInfo.append(child.read())
        info = child.read()
        exeInfo.append(info)
        child.close()
        print info
    for i in exeInfo:
        if "No" in i:
            return 0
    return 1
if __name__ == "__main__":
    print "main"
    scp("host.list","/tmp", "file.list")
