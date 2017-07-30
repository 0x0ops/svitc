# -*- coding: utf8 -*-
import time
import re
import scrapy
from scrapy import FormRequest
from scrapy.spiders import BaseSpider
from sinhvienit.items import SinhvienitItem

class MySpyder(BaseSpider):
    name = "svitspider"
    allowed_domains = ["sinhvienit.net"]
    start_urls = ["http://sinhvienit.net/forum/thu-thuat-bai-viet-huong-dan.83/"]

    def parse(self, response):
        request = FormRequest.from_response(response,
                                            formdata={"vtlai_firewall_postcontent": ""},
                                            callback=self.parse_subforum)
        yield request
    def parse_subforum(self, response):
        urls = response.xpath("//h3[@class='threadtitle']//@href").extract()
        #print "..........................."
        for url in urls:
            full_url = response.urljoin(url)
            request = scrapy.Request(full_url, callback=self.parse_thread)
            time.sleep(1)
            yield request

    def parse_thread(self, response):
        item = SinhvienitItem()
        item['url'] = response.url
        title = response.xpath("//title/text()").extract()
        item['title'] = title
        #author = response.xpath("//a[@class='userdesc']//text()").extract()
        #item['author'] = author

        # Get list member on page
        members = response.xpath("//div[@class='username']//strong//text()").extract()
        dic_member = {}
        for i in range(0, len(members)):
            dic_member[i] = members[i]
        item['author'] = dic_member[0]
        del dic_member[0]
        item['member_comment'] = dic_member

        # Get topic content and all comment in first page
        posts = response.xpath('//div[@class="firstpostbody"]//article[@class="articleBody"]')
        dic_content = {}
        print "..........................."
        for i in range(0, len(posts)):
            post_content = posts[i].xpath('blockquote//text()').extract()
            dic_content[i] = post_content
        item['topic_content'] = dic_content[0]
        del dic_content[0]
        item['comment'] = dic_content
        print "..........................."

        yield item

    #def content_fomat(self, response):

    def date_time(self, dat):
        date_regex = re.compile('\d{1,}[-/]\d{1,}[-/]\d{4}')
        time_regex = re.compile('\d{1,}[:]\d{1,}')
        return date_regex.findall(dat)[0] + " | " + time_regex.findall(dat)[0]