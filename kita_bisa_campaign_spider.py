import scrapy


class QuotesSpider(scrapy.Spider):
    name = "kitabisa"
    start_urls = [
        'https://kitabisa.com/explore/all',
    ]

    def parse(self, response):
        for card in response.css('.m-card--on-desktop'):
            yield {
                'img' : card.css('img.m-card__thumb').xpath('@src').extract_first(),
                'title': card.css('h3.m-card__title::text').extract_first(),
                'campaigner': card.css('.m-card__subtitle-wording > span::text').extract_first(),
                'verified': card.css('.m-card__check').xpath('@src').extract_first(),
                'short_desc': card.css('p.m-card__desc::text').extract_first(),
                'stats': card.css('.m-card__stats::text').extract()
                # 'text': card.css('span.text::text').extract_first(),
                # 'author': card.xpath('span/small/text()').extract_first(),
            }

        next_page = response.xpath('//ul[contains(@class, "paging-number")]//li[last()-1]/a/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
