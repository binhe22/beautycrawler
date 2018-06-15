BeautyCrawler
=============
* https://github.com/binhe22/flyer  分布式的启动和数据传输工具
* https://github.com/binhe22/RequestsProxy  requests用的http代理
* https://github.com/binhe22/beautycrawler gevent 单进程爬虫
* 具体题目22mm.cc: https://github.com/binhe22/beautycrawler/tree/22mm.cc

##### 将三个组合起来，就是一个支持自动发现代理，使用多机，多核心，单进程内使用gevent的多级并行的爬虫。

#### 性能：
可以突破GIL限制，利用多核心，多机。进程内部使用gevent进行并行化。现在问题在于，redis是单线程的，所以性能瓶颈在redis。由于我这里没有强约束的数据关系，所以redis的数据同步问题在这显得不是那么重要。

#### 拓展性：

只需要重写寻找图片url的方法就可以移植到其他美女网站。
主要重写保存方式和寻找保存url的规则的方法，理论就可以移植到任何网站。

#### 稳定性：

有单独的协程处理error，并将错报的url运行完成。

现在比较晕了，我也不知道该怎么说了，我先睡会再详细说^_^

You can select db, and set programExit 1, to make the cluster stop, if the ctrl-c does not work

72000-73000张照片，7G多，最快的时候12分钟可以爬完整个流程，包括网页解析等等。

#### 如果要跑需要改参数：


config.py 很多，可以根据意思修改
redisconfig.py 用来做flyer的redis的配置
host.list 需要运行的node，每行表示添加一个进程到node，所以可以添加n个进程到node
file.list  运行文件可能会用到的文件，包括自身，同步到每个node
--e 指明要运行的文件

修改redis配置，调整fils.list 和 host.list
```
./beautycrawler.py --e crawler.py
```
