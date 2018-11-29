# -*- coding: utf-8 -*-
import re
import os
import json
import datetime
try:# 为兼容py2和py3，在try中导入
    from urllib import parse #py3
except:
    import urlparse as parse #py2

import scrapy
from scrapy.loader import ItemLoader
# from items import ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = "zhihuSpider"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    #question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url , url) for url in all_urls]
        all_urls=filter(lambda url:True if url.startswith("https") else False , all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/.*|$)" , url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                print('________________________________')
                print(request_url)
                print(question_id)

    def parse_question(self, response):
        """
        处理question页面， 从页面中提取出具体的question item
        :param response:
        :return:
        """
        pass

    def parse_answer(self, reponse):
        """
        处理回答
        :param reponse:
        :return:
        """
        pass

    def start_requests(self):
        """
        覆写start_requests方法，使用selenium实现登录功能，获取cookie
        :return:
        """
        from selenium import webdriver
        project_dir = os.getcwd()#返回当前工作目录
        chromeDriver = os.path.join(project_dir, 'chromeDriver', 'chromedriver.exe')# 取得驱动所在目录
        browser = webdriver.Chrome(executable_path=chromeDriver)
        browser.get("https://www.zhihu.com/signin")
        settings = self.settings  # 获取settings中的配置
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
            settings['ZHIHU_ACCOUNT'])
        browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
            settings['ZHIHU_PASSWORD'])
        browser.find_element_by_css_selector(
            ".Button.SignFlow-submitButton").click()
        import time
        time.sleep(10)
        Cookies = browser.get_cookies()
        print(Cookies)
        cookie_dict = {}
        import pickle
        for cookie in Cookies:
            # 写入文件
            cookieDir = os.path.join(project_dir, cookie['name'] + '.zhihu')
            f = open(cookieDir, 'wb')
            pickle.dump(cookie, f)
            f.close()
            cookie_dict[cookie['name']] = cookie['value']
        browser.close()
        return [scrapy.Request(url=self.start_urls[0],headers=self.headers , dont_filter=True, cookies=cookie_dict)]