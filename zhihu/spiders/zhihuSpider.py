# -*- coding: utf-8 -*-
import re
import os
import json
import datetime
from zhihu.items import ZhihuQuestionItem
from zhihu.items import ZhihuAnswerItem
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
    start_urls = ['https://www.zhihu.com/api/v3/feed/topstory/recommend?session_token=bc86575b6393e3ab19c3223335becf89&desktop=true&limit=7&action=down&after_id=0']

    #question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&sort_by=default"

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
        question_json = json.loads(response.text)

        for question in question_json['data']:
            try:
                question_id = question['target']['question']['id']#有时候出现广告，会出现异常
            except:
                continue
            question_url = 'https://www.zhihu.com/question/'+str(question_id)
            print(question_url)
            yield scrapy.Request(question_url, headers=self.headers, callback=self.parse_question)
        is_end_page = question_json['paging']['is_end']
        if not is_end_page:
            next_page_url = question_json['paging']['next']
            yield scrapy.Request(next_page_url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        """
        处理question页面， 从页面中提取出具体的question item
        :param response:
        :return:
        """
        if "QuestionHeader-title" in response.text:
            # 处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            item_loader.add_xpath("watch_user_num" , '//*[@id="root"]/div/main/div/div[1]/div[2]/div[1]/div[2]/div/div/div/button/div/strong/text()')
            item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

            question_item = item_loader.load_item()
        else:
            # 处理老版本页面的item提取
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            ######################### 存在两种情况时的标签内容提取#################################
            item_loader.add_xpath("title",
                                  "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num",
                                  "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id , 20 , 0),
                             headers=self.headers , callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        """
        处理问题回答
        :param reponse:
        :return:
        """
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)


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