
import os
import pathlib
import urllib.parse

import scrapy
from scrapy.http import Request


class CheckFileLinksSpider(scrapy.Spider):
    name = "check_file_links"
    start_urls = [
        'http://library.bjp.org/jspui/browse?type=title&sort_by=1&order=ASC&rpp=2642&etal=-1&null=&offset=0'
        # pathlib.Path(os.path.abspath('books-list.html')).as_uri()
    ]

    def parse(self, response):
        book_page_links = response.xpath("//td[@headers='t2']//@href")
        yield from response.follow_all(book_page_links, self.parse_book_page)

    def parse_book_page(self, response):
        file_relative_url = response.xpath(
            "//td[@headers='t1']//@href").get(default='').strip()
        file_abs_url = response.urljoin(file_relative_url)
        filename = urllib.parse.unquote(file_abs_url.split('/')[-1])
        yield {
            'ISSUEDT': extract_with_css('td.metadataFieldValue.dc_date_issued::text'),
            'title': extract_with_css('td.metadataFieldValue.dc_title::text'),
            'titleurl': response.request.url,
            'author': extract_with_css('.author::text'),
            'authorurl': response.urljoin(extract_with_css('.author::attr(href)')),
            'collection': response.xpath(
                "//td[contains(text(), 'Appears in Collections:')]"
                + "/following-sibling::td[1 and @class='metadataFieldValue']"
                + "//a//text()").get(default='').strip(),
            'collectionurl': response.urljoin(response.xpath(
                "//td[contains(text(), 'Appears in Collections:')]"
                + "/following-sibling::td[1 and @class='metadataFieldValue']"
                + "//@href").get(default='').strip()),
            'filename': filename,
            'fileurl': file_abs_url
        }
