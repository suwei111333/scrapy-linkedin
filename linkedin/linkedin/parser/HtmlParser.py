from linkedin.items import PersonProfileItem
import random

class HtmlParser:    
    @staticmethod
    def extract_person_profile(hxs):
        personProfile = PersonProfileItem()
        personProfile['name'] = {"first_name":"wei chen", "last_name":"chen"}
        return personProfile
