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

class LinkedinspiderSpider(CrawlSpider):
    name = 'LinkedinSpider'
    allowed_domains = ['linkedin.com']
    start_urls = [
                  "http://www.linkedin.com/directory/people/a.html",
                  "http://www.linkedin.com/directory/people/b.html",
                  "http://www.linkedin.com/directory/people/c.html",
                  "http://www.linkedin.com/directory/people/d.html",
                  "http://www.linkedin.com/directory/people/e.html",
                  "http://www.linkedin.com/directory/people/f.html",
                  "http://www.linkedin.com/directory/people/g.html",
                  "http://www.linkedin.com/directory/people/h.html",
                  "http://www.linkedin.com/directory/people/i.html",
                  "http://www.linkedin.com/directory/people/j.html",
                  "http://www.linkedin.com/directory/people/k.html",
                  "http://www.linkedin.com/directory/people/l.html",
                  "http://www.linkedin.com/directory/people/m.html",
                  "http://www.linkedin.com/directory/people/n.html",
                  "http://www.linkedin.com/directory/people/o.html",
                  "http://www.linkedin.com/directory/people/p.html",
                  "http://www.linkedin.com/directory/people/q.html",
                  "http://www.linkedin.com/directory/people/r.html",
                  "http://www.linkedin.com/directory/people/s.html",
                  "http://www.linkedin.com/directory/people/t.html",
                  "http://www.linkedin.com/directory/people/u.html",
                  "http://www.linkedin.com/directory/people/v.html",
                  "http://www.linkedin.com/directory/people/w.html",
                  "http://www.linkedin.com/directory/people/x.html",
                  "http://www.linkedin.com/directory/people/y.html",
                  "http://www.linkedin.com/directory/people/z.html"
                  ]

    rules = (
        #Rule(SgmlLinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse(self, response):
        """
        default parse method, rule is not useful now
        """
        hxs = HtmlXPathSelector(response)
        index_level = self.determine_level(response)
        if index_level in [1, 2, 3, 4]:
            self.save_to_file_system(index_level, response)
            relative_urls = self.get_follow_links(index_level, hxs)
            if relative_urls is not None:
                for url in relative_urls:
                    yield Request(url, callback=self.parse)
        elif index_level == 5:
            personProfile = HtmlParser.extract_person_profile(hxs)
            linkedin_id = self.get_linkedin_id(response.url)
            linkedin_id = UnicodeDammit(urllib.unquote_plus(linkedin_id)).markup
            if linkedin_id:
                personProfile['_id'] = linkedin_id
                personProfile['url'] = UnicodeDammit(response.url).markup
                yield personProfile
    
    def determine_level(self, response):
        """
        determine the index level of current response, so we can decide wether to continue crawl or not.
        level 1: people/[a-z].html
        level 2: people/[A-Z][\d+].html
        level 3: people/[a-zA-Z0-9-]+.html
        level 4: search page, pub/dir/.+
        level 5: profile page
        """
        import re
        url = response.url
        if re.match(".+/[a-z]\.html", url):
            return 1
        elif re.match(".+/[A-Z]\d+.html", url):
            return 2
        elif re.match(".+/people/[a-zA-Z0-9-]+.html", url):
            return 3
        elif re.match(".+/pub/dir/.+", url):
            return 4
        elif re.match(".+/search/._", url):
            return 4
        elif re.match(".+/pub/.+", url):
            return 5
        return None
    
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
        
    def get_follow_links(self, level, hxs):
        if level in [1, 2, 3]:
            relative_urls = hxs.select("//ul[@class='directory']/li/a/@href").extract()
            relative_urls = ["http://linkedin.com" + x for x in relative_urls]
            return relative_urls
        elif level == 4:
            relative_urls = self.get_profile_from_search_page(hxs)
            relative_urls = ["http://linkedin.com" + x for x in relative_urls]
            return relative_urls

    def create_path_if_not_exist(self, filePath):
        if not path.exists(path.dirname(filePath)):
            os.makedirs(path.dirname(filePath))
            
    def get_profile_from_search_page(self, hxs):                  
        """
        parse search page to get profile links
        """
        relative_urls = hxs.select("//ol[@id='result-set']/li/div/a/@href").extract()
        cur_page = hxs.select("//p[@class='page'/strong/text()").extract()[0]
        if int(cur_page) == 1:
            page_urls = hxs.select("//p[@class='page']/a/@href").extract()
            relative_urls.extent(page_urls);
        return relative_urls
