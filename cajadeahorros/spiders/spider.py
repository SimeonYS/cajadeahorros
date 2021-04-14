import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CcajadeahorrosItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'

class CcajadeahorrosSpider(scrapy.Spider):
	name = 'cajadeahorros'
	start_urls = ['https://www.cajadeahorros.com.pa/categoria/noticias/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="btn btn-secondary"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//script[@type="application/ld+json"]/text()').get()
		date = json.loads(date)
		date = date['@graph'][2]['datePublished'].split('T')[0]
		title = response.xpath('(//h1)[last()]/text()').get()
		content = response.xpath('//div[@class="entry-content default-page"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CcajadeahorrosItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
