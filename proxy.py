#coding:utf8
import requests
import re
import base64

headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip,deflate,sdch',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Connection':'keep-alive',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'
        }

def startRun():
    httpTmp = []
    http = []
    url = 'http://proxy.ipcn.org/proxylist.html'
    r = requests.get(url, headers=headers)
    httpTmp = re.findall('\d+\.\d+\.\d+\.\d:\d+', r.text)
    for i in httpTmp:
        http.append("http://"+str(i))
    print http
    return http


if __name__ == "__main__":
    startRun()
