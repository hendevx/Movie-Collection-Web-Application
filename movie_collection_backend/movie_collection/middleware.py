from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

class RequestCounterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        cache.incr('request_count')
    
class RequestCounterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if cache.get('request_count') is None:
            cache.set('request_count', 0)
        cache.incr('request_count')
