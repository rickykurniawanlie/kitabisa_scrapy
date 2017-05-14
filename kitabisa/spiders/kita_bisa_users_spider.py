import scrapy
from scrapy import signals
from scrapy.spider import Spider
from scrapy.xlib.pydispatch import dispatcher

class UsersSpider(scrapy.Spider):
	handle_httpstatus_list = [404] 	
	name 		= "users"
	url 		= 'https://kitabisa.com/orang-baik/'
	# first id for range brute force
	userId 		= 99999
	# last id for range brute force
	maxUserId	= 100002

	def start_requests(self):
		self.failed_urls = []
		url = self.url + str(self.userId)
		yield scrapy.Request(url, self.parse)
		dispatcher.connect(self.handle_spider_closed, signals.spider_closed)	

	def parse(self, response):
		if response.status == 404:
			self.crawler.stats.inc_value('failed_url_count')
			failed_url = response.url[32:]
			self.failed_urls.append(failed_url)

		# campaignSupportedExist = 'Campaign Didukung' in tabs_nav[0].strip()
		# campaignRaisedExist = 'Campaign Dimulai' in tabs_nav[0].strip()
		statusInfo 		= response.css('div.user-status-info div.item-text::text').extract()
		containerDonasi = response.css('div#donasi a.m-card__href::attr("href")').extract()
		campaignDonasi	= [campaign[21:] for campaign in containerDonasi]
		containerProyek = response.css('div#proyek a.m-card__href::attr("href")').extract()
		campaignProyek	= [campaign[21:] for campaign in containerProyek]
		# Empty array , then 404 page
		if statusInfo:
			resultDict 	= {
				'id'	: self.userId,
				'nama' 	: statusInfo[0].strip(),
				'to'	: statusInfo[1].strip()[-10:],
				'ma'	: statusInfo[2].strip()[-10:],
			}
			if containerProyek: 
				resultDict['campaignDimulai'] = campaignProyek
			if containerDonasi:
				resultDict['campaignDidanai'] = campaignDonasi

			yield resultDict

		self.userId = self.userId + 1;
		nextPage 	= self.url + str(self.userId)
		if self.userId < self.maxUserId:
			next_page = response.urljoin(nextPage)
			yield scrapy.Request(next_page, self.parse)

	def handle_spider_closed(self,spider, reason):
		self.crawler.stats.set_value('failed_urls', ','.join(spider.failed_urls))

	def process_exception(self, response, exception, spider):	
		ex_class = "%s.%s" % (exception.__class__.__module__, exception.__class__.__name__)
		self.crawler.stats.inc_value('downloader/exception_count', spider=spider)
		self.crawler.stats.inc_value('downloader/exception_type_count/%s' % ex_class, spider=spider)
