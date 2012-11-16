from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy import log
from linkedin.items import LinkedinItem, PersonProfileItem
from os import path
from linkedin.parser.HtmlParser import HtmlParser
import os
import urllib
from bs4 import UnicodeDammit
from linkedin.db import MongoDBClient

class LinkedinspiderSpider(CrawlSpider):
    name = 'LinkedinSpider'
    allowed_domains = ['linkedin.com']
    start_urls = []

    rules = (
        #Rule(SgmlLinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def __init__(self):
        """
        new approach to crawl
        1. get top name from aminer
        2. search in linkedin
        3. parse result(if only 1 match, go to step 4)
        4. normal profile page

        link: http://www.linkedin.com/pub/dir/?first=%22hang%22&last=%22li%22&search=Search
        """
        self.first_level_url_db_client = MongoDBClient("first_level_url")
        urls = self.first_level_url_db_client.walk()
        self.start_urls = [x['url'] for x in urls] 
        
    def parse(self, response):
        response = response.replace(url=HtmlParser.remove_url_parameter(response.url))
        hxs = HtmlXPathSelector(response)
        html_type = self.detect_response_type(response)
        if html_type == 1:
            # search result page
            urls = self.get_search_result_links(hxs)
            if urls is not None:
                for url in urls:
                    yield Request(url, callback=self.parse)
        elif html_type == 2:
            # profile page
            personProfile = HtmlParser.extract_person_profile(hxs)
            linkedin_id = self.get_linkedin_id(response.url)
            linkedin_id = UnicodeDammit(urllib.unquote_plus(linkedin_id)).markup
            if linkedin_id:
                personProfile['_id'] = linkedin_id
                personProfile['url'] = UnicodeDammit(response.url).markup
                yield personProfile
        else:
            # error
            log.msg("Abnormal url: %s" % response.url, log.CRITICAL)
    
    def get_search_result_links(self, hxs):
        return hxs.select("//ol[@id='result-set']/li/h2/strong/a/@href").extract()
    
    def detect_response_type(self, response):
        import re
        url = response.url
        if re.match(".+/pub/dir/.+", url):
            return 1
        elif re.match(".+/pub/.+", url):
            return 2
        return -1
    
    def save_to_file_system(self, level, response):
        """
        save the response to related folder
        """
        if level in [1, 2, 3, 4, 5]:
            fileName = self.get_clean_file_name(level, response)
            if fileName is None:
                return
            
            fn = path.join(self.settings["DOWNLOAD_FILE_FOLDER"], str(level), fileName)
            self.create_path_if_not_exist(fn)
            if not path.exists(fn):
                with open(fn, "w") as f:
                    f.write(response.body)
    
    def get_clean_file_name(self, level, response):
        """
        generate unique linkedin id, now use the url
        """
        url = response.url
        if level in [1, 2, 3]:
            return url.split("/")[-1]
        
        linkedin_id = self.get_linkedin_id(url)
        if linkedin_id:
            return linkedin_id
        return None
        
    def get_linkedin_id(self, url):
        find_index = url.find("linkedin.com/")
        if find_index >= 0:
            return url[find_index + 13:].replace('/', '-')
        return None

    def create_path_if_not_exist(self, filePath):
        if not path.exists(path.dirname(filePath)):
            os.makedirs(path.dirname(filePath))
            
