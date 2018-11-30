# zhihuSpider

---
## 1. 爬虫介绍
本爬虫用于爬取知乎网站问题、回答的相关字段信息，问题的标题、内容、发布时间、话题、回答数量、评论数、点击数、关注数等字段，及对该问题回答的内容，作者、点赞数、评论数、回答时间等等字段信息。可用于对社会话题、热点进行数据分析。
## 2. 技术路线
### 2.1 采用技术
本爬虫采用技术如下：
- **scrapy框架**：
本爬虫基于当下最热门的爬虫框架——scrapy进行编写。
- **css选择器**：爬虫中结构化数据采用css选择器进行提取。
- **mysql数据**库：采集获得结构化数据使用scrapy自带的twisted异步存储的方式存到MySQL数据库中。
- **selenium模拟浏览器**：对于知乎账号登录部分，采用的是selenium模拟浏览器进行登录，获取cookie。
### 2.2 采集思路
##### 1）一级页面
一级页面是指所有知乎问题所在的页面，可以采集到所有的问题。该页面是动态更新的，每次下拉进度条，知乎会自动在一级页面加载出更多的问题。通过分析发现，一级页面每次动态加载都是以一个web接口的方式进行数据交互，且交互传输的数据中不但有新加载的问题还有下一次动态加载的接口链接，所以，每次采集新的问题四，只需要在爬虫parse方法中下一次接口发送request即可。
##### 2）二级页面
二级页面是指问题的详细页面，二级页面的入口url可以根据知乎域名和一级页面中提取的问题id组合获得。二级页面中包含问题的所有详细信息，本爬虫采用css选择器进行信息提取。
##### 3）三级页面
三级页面是对问题的回答的详细信息页面，事实上，该页面也是动态加载的。每次下拉进度条都会加载最新的回答，经过分析发现，该过程也是以接口方式进行，所以，对接口传输的数据进行采集即可。
### 2.3 数据库设计
本爬虫数据库包含两张表，分别用于存放问题的相关字段信息和回答的相关字段信息。表结构如下：
zhihu_question:
![zhihu_question表结构设计](https://github.com/ChenHuabin321/zhihuSpider/blob/master/zhihu/readme_image/zhihu_question.png)
zhihu_answer:
![zhihu_answer表结构设计](https://github.com/ChenHuabin321/zhihuSpider/blob/master/zhihu/readme_image/zhihu_answer.png)
## 3. 下载

下载源码

git方式下载：git@github.com:ChenHuabin321/zhihuSpider.git

或者直接到下载zip源码包，地址为：https://github.com/ChenHuabin321/zhihuSpider

安装依赖

PyMySQL==0.9.2

Scrapy==1.5.0

Twisted==18.4.0

selunium==3.14.0

数据库配置

以下是settings.py中的默认数据库配置，可进行修改为你的数据库配置：

MYSQL_HOST = '192.168.56.101'#主机

MYSQL_PASSWORD = '123456'#密码

MYSQL_DBNAME = 'article_spider'#数据库名

另外需要配置你的知乎账号密码：

#知乎账号配置

ZHIHU_ACCOUNT = '18888888888'#知乎账号

ZHIHU_PASSWORD = '123456789'#知乎密码

## 4. 采集结果展示
经过测试3小时左右采集了330多个知乎问题，32万条回答，部分数据如下图所示：
知乎问题：
![image](https://github.com/ChenHuabin321/zhihuSpider/blob/master/zhihu/readme_image/%E7%9F%A5%E4%B9%8E%E9%97%AE%E9%A2%98.png)
问题回答：
![image](https://github.com/ChenHuabin321/zhihuSpider/blob/master/zhihu/readme_image/%E7%9F%A5%E4%B9%8E%E5%9B%9E%E7%AD%94.png)
