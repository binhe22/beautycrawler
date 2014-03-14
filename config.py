config = {"redisIp":"127.0.0.1", #redis ip
            "redisPort":6379, #redis port
            "redisDb":5, #redis db
            "redisPassword":'', #redis password
            "host":["22mm.cc","meimei22.com"], #only crawl the url in this list, will not crawl out
            "seed":["http://www.22mm.cc/mm/qingliang/", "http://www.22mm.cc/",
                "http://www.22mm.cc/mm/suren/"], #the start
             "chunk_size":256, #save file chunk_size
        	 "proxiesNum":50, #the proxy num used
        	 "proxyOn":1, #if use proxy, if set 0,will ignore proxiesNum
        	 "crawlNum":50, #how many greenlet for crawl
        	 "saveNum":50, #how many greenlet for save
        	 "crawlErrorHandleNum":5,
        	 "saveErrorHandleNum":5,
        	"redisCrawlingKey":"crawling", #the key in redis to save the list
        	 "redisSavingKey":"saving",
        	 "redisCrawledKey":"crawled",
        	 "redisSavedKey":"saved",
        	 "redisCrawlErrorKey":"cralwerror",
        	 "redisSaveErrorKey":"saveerror",
        	 "timeout":10, #crawl time out
             "outDir":"/home/lemon/Beatuty/", # nedd /
             "saveLimit":-1,  #how many resource to save, -1 nolimited
            }
headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Connection':'keep-alive',
            'Host':"http:/www.22mm.cc/",
            'Referer':'http://www.22mm.cc/mm/suren/PiaHaimeHmHPaHJHC.html',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'
            }#you can define the custom headers


