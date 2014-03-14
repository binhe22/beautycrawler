#!/usr/bin/env python
#coding=utf-8
import flyer
import time
import gevent
if __name__ == "__main__":
    t = flyer.flyer()
    id = t.start()
    for i in range(100):
        print id, i
        gevent.sleep(0.1)

