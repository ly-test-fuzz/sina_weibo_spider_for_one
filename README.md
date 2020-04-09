# sina_weibo_spider_for_one
运行抓取一个指定用户最新微博的爬虫 ，并且使用qqbot自动提醒用户


- 环境
  - python
    - requeirements.txt
  - 酷 q air
    - docker 启动指令
      - docker run -ti --rm --name cqhttp-test -d -v $(pwd)/coolq:/home/user/coolq -p 9000:9000 -p 5700:5700 -p 8081:8081 -e  VNC_PASSWD=vnc_password -e COOLQ_ACCOUNT=target_qq_account -e CQHTTP_POST_URL=http://x.x.x.x:8081 -e CQHTTP_SERVE_DATA_FILES=yes richardchien/cqhttp:latest
    - cqhttp 插件
  - 一个可以登录的微博账号
    - 由于此爬虫调用的是 微博 手机端接口，所以对账号的要求高一些 ， 目前测出的条件是需要一个常用的网络环境。
      - 账号登录被检测 ， 报错信息为 系统错误
- 参考
  - 微博登录
    - https://github.com/rockgarden/website_crawl/blob/c9a44ffe117595e5cad04d6ffe6520cdb064521f/sina/sina_login_phone.py
  
