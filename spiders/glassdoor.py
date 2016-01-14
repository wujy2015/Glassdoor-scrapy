# -*- coding: UTF-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request,FormRequest
from test1.items import Test1Item
import json
import re

class WestDoorSpider(Spider):
	name = 'door'
	allowed_domains = ['glassdoor.com']

	def start_requests(self):
		yield FormRequest('https://www.glassdoor.com/profile/ajax/loginAjax.htm',
			formdata={'isCaptchaVisible':'false',
			'password':'',
			'recaptcha_challenge_field':'',
			'recaptcha_response_field':'',
			'rememberMe':'true',
			'u':'http://www.glassdoor.com/Reviews/Facebook-Reviews-E40772_P7.htm?filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME&filter.employmentStatus=UNKNOWN',
			'userOriginHook	':'HEADER_SIGNIN_LINK',
			'username':''},
			callback = self.parse_login)

	def parse_login(self, response):
		# urls = ['http://www.glassdoor.com/Reviews/Facebook-Reviews-E40772.htm'
		# 'http://www.glassdoor.com/Reviews/eBay-Reviews-E7853.htm',
		# 'http://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm',
		# 'http://www.glassdoor.com/Reviews/LinkedIn-Reviews-E34865.htm',
		# ]
		urls = ['http://www.glassdoor.com/Reviews/us-reviews-SRCH_IL.0,2_IN1.htm']
		for url in urls:
			yield Request(url, callback = self.parse_page)

	def parse_page(self, response):
		firms = response.xpath("//a[@class='eiCell cell reviews']/@href").extract()
		for firm in firms:
			yield Request('http://www.glassdoor.com'+firm, callback = self.parse_item)
		next_page = response.xpath("//li[@class='next']//@href").extract()
		next_page = next_page[0] if next_page else None
		if next_page is not None:
			yield Request('http://www.glassdoor.com'+next_page, callback = self.parse_page)

	def parse_item(self, response):
		sel = response.xpath('//ol/li[contains(@id, "empReview")]')
		for review in sel:
			item = Test1Item()
			item['title'] = ''.join(review.xpath('.//h2/a/span[@class = "summary "]/text()').extract())
			item['link'] = ''.join(review.xpath('.//h2[@class="h2 summary strong tightTop"]/a/@href').extract())
			item['job_title'] = ''.join(review.xpath('.//span[@class = "authorJobTitle middle"]/text()').extract())
			item['work_life_balance'] = ''.join(review.xpath(".//div[text()='Work/Life Balance']/following-sibling::node()/@title").extract())
			item['location'] = ''.join(review.xpath('.//span[@class="authorLocation i-loc middle"]/text()').extract())
			item['time'] = ''.join(review.xpath('.//time[@class="date subtle small"]/text()').extract())
			item['pos'] = ''.join(review.xpath('.//p[contains(@class, "pros")]/text()').extract() + review.xpath('.//p[contains(@class, "pros")]/span[@class = "moreEllipses"]/following-sibling::node()/span/text()').extract())
			item['cons'] = ''.join(review.xpath('.//p[contains(@class, "cons")]/text()').extract() + review.xpath('.//p[contains(@class, "cons")]/span[@class = "moreEllipses"]/following-sibling::node()/span/text()').extract())
			item['advice'] = ''.join(review.xpath('.//p[contains(@class, "adviceMgmt")]/text()').extract())
			item['overal_rating'] = ''.join(review.xpath('.//span[@class = "gdStars gdRatings sm margRt"]/span[@class = "rating notranslate_title"]//@title').extract())
			item['Culture_Values'] = ''.join(review.xpath('.//div[text() = "Culture & Values"]/following-sibling::node()/@title').extract())
			item['Career_Opportunities'] = ''.join(review.xpath('.//div[text() = "Career Opportunities"]/following-sibling::node()/@title').extract())
			item['Comp_Benefits'] = ''.join(review.xpath('.//div[text() = "Comp & Benefits"]/following-sibling::node()/@title').extract())
			item['Senior_Management'] = ''.join(review.xpath('.//div[text() = "Senior Management"]/following-sibling::node()/@title').extract())
			yield item

		next_url = response.xpath("//li[@class='next']//@href").extract()
		next_url = next_url[0] if next_url else None
		if next_url is not None:
			yield Request('http://www.glassdoor.com'+next_url, callback = self.parse_item)