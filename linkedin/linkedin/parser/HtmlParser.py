from linkedin.items import PersonProfileItem
from bs4 import UnicodeDammit
import random

class HtmlParser:    
    @staticmethod
    def extract_person_profile(hxs):
        personProfile = PersonProfileItem()
        ## Person name
        nameField = {}
        nameSpan = hxs.select("//span[@id='name']/span")
        if nameSpan and len(nameSpan) == 1:
            nameSpan = nameSpan[0]
            givenNameSpan = nameSpan.select("span[@class='given-name']")
            if givenNameSpan and len(givenNameSpan) == 1:
                givenNameSpan = givenNameSpan[0]
                nameField['given_name'] = givenNameSpan.select("text()").extract()[0]
            familyNameSpan = nameSpan.select("span[@class='family-name']")
            if familyNameSpan and len(familyNameSpan) == 1:
                familyNameSpan = familyNameSpan[0]
                nameField['family_name'] = familyNameSpan.select("text()").extract()[0]
            personProfile['name'] = nameField
        else:
            return None
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
                    personProfile['also_view'] = alsoViewProfileList
        return personProfile

    @staticmethod
    def get_also_view_item(dirtyUrl):
        item = {}
        url = HtmlParser.remove_url_parameter(dirtyUrl)
        item['linkedin_id'] = url 
        item['url'] = HtmlParser.get_linkedin_id(url)
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
        
