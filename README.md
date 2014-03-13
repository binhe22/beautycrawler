Beautyimg
=========
###What Is It
It is a distributed crawler with the help of flyer(in another repo). 

###How Does It Works

It will include the modules -- proxy modules(auto find web proxy), distributed task modules(flyer), crawler modules(you can define the crawling rules by rewriting some methods), and those modules can work respectively.

In one process, it use gevent to speedup.

###How to Use
For exmaple, if you want to crawl others beauty websites, you can just inherit the crawl class and rewirte the findSaveUrl methods.

If you want to crawl any other websites, you can just inherit the crawl class and rewrite methods findNextUrl ,findSaveurl to define the rules to put the url in crawling queue and put the url in saving quene, rewrite method goSave to define how to save the resource(put in mysql, redis or just save in the disk). 
