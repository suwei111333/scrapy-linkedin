from linkedin.items import PersonProfileItem
from bs4 import UnicodeDammit
import random

class HtmlParser:    
    @staticmethod
    def extract_person_profile(hxs):
        personProfile = PersonProfileItem()
        personProfile['name'] = {"first_name":"wei chen", "last_name":"chen"}
        
        ## Also view
        alsoViewProfileList = []
        divExtra = hxs.select("//div[@id='extra']")
        if divExtra and len(divExtra) == 1:
            divExtra = divExtra[0]
            divAlsoView = divExtra.select("//div[@class='leo-module mod-util browsemap']")
            if divAlsoView and len(divAlsoView) == 1:
                divAlsoView = divAlsoView[0]
                alsoViewList = divAlsoView.select("div[@class='content']/ul/li/strong/a/@href").extract()
                if alsoViewList:
                    for alsoViewItem in alsoViewList:
                        alsoViewItem = UnicodeDammit(alsoViewItem).markup
                        item = HtmlParser.get_also_view_item(alsoViewItem)
                        alsoViewProfileList.append(item)
        return personProfile

    @staticmethod
    def get_also_view_item(dirtyUrl):
        item = {}
        item['linkedin_id'] = HtmlParser.remove_url_parameter(dirtyUrl)
        item['url'] = HtmlParser.get_linkedin_id(dirtyUrl)
        return item
        
        
    @staticmethod
    def remove_url_parameter(url):
        url = url.rsplit("?", 1)
        return url[0]
    
    @staticmethod
    def get_linkedin_id(url):
        find_index = url.find("linkedin.com/")
        if find_index >= 0:
            return url[find_index + 13:].replace('/', '-')
        return None
        
