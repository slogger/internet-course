'''
Implement a simple dns cache module to reduce dns resolve time. Also avoid
too many hit to DNS server. This module might not be thread safe.
'''

# Refresh DNS by 1 hr.
DNS_REFRESH_TIME = 3600

import socket
import datetime
# from util.decorator import Singleton
import urllib.parse


class DNSError(Exception):
    pass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DNSCache(object, metaclass=Singleton):
        def __init__(self):
                self.cache = {}

        def get_addr(self, hostname):
                '''
                Get address info from hostname. DNSCache
                will maintain a dict of hostanmes.
                For each host name, the value are in the form (addr, timestamp)
                '''
                print(self.cache)
                print(hostname)
                if hostname in self.cache.keys():
                        addr, timestamp = self.cache[hostname]
                        now = datetime.datetime.now()
                        age = now - timestamp
                        if age.seconds > DNS_REFRESH_TIME:
                                # Refresh DNS cache.
                                return _get_addr(hostname)
                        else:
                                return addr
                else:
                        return self._get_addr(hostname)

        def _get_addr(self, hostname):
                try:
                        result = socket.getaddrinfo(hostname, None)
                except Exception as e:
                        raise DNSError(e)
                if len(result) > 0:
                        self.cache[hostname] = (
                            result[0][4][0], datetime.datetime.now())
                        return result[0][4][0]
                else:
                        raise DNSError('DNS returns nothing.')


def ipify(url):
        parts = list(urllib.parse.urlsplit(url))
        c = DNSCache()
        parts[1] = c.get_addr(parts[1])
        return urllib.parse.urlunsplit(parts)

# Unit Test & Sample
if __name__ == "__main__":
        dns = DNSCache()

        # Should raise DNSError.
        try:
                print((ipify('http://www.googlerrrr.com')))
        except DNSError as e:
                print(e)

        # from util.timing import Timing
        # First dns resolve for www.google.com.
        # t = Timing()
        # with t:
        print((ipify('http://www.google.com')))
        # print(t)

        # with t:
        print((ipify('http://www.google.com/?a=x')))
        # print(t)
