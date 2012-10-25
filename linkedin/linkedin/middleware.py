from scrapy import log

"""
Custom proxy provider. 
"""
class CustomHttpProxyMiddleware(object):
    def process_request(self, request, spider):
        # TODO implement complex proxy providing algorithm
        return None
