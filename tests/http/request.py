import unittest
from catscore.http.request import CatsRequest
from catscore.http.tor import Tor

class TestCatsRequest(unittest.TestCase):
    def test_get(self):
        request:CatsRequest = CatsRequest()
        responseHtml = request.get(url="https://yahoo.co.jp", response_content_type="html")
        responseJson = request.get(url="https://api.rescala.jp/current_stock_info", response_content_type="json")
        print(responseJson)
        request.close()
        
    def tor(self):
        """[python -m unittest tests.http.request.TestCatsRequest.tor
        https://lets-hack.tech/programming/languages/python/tor/
        must execute pip install pysocks
        # Install for mac
        brew install tor
        ## start 
        brew services start tor
        ## stop
        brew services stop tor
        ]
        """

        proxy = None
        request:CatsRequest = CatsRequest(proxy=proxy)
        print(f"without tor: {request.get_global_info()['ip']}")
        request.close()
        
        proxy = {'http':'socks5://127.0.0.1:9050','https':'socks5://127.0.0.1:9050'}
        request:CatsRequest = CatsRequest(proxy=proxy)
        print(f"with tor: {request.get_global_info()['ip']}")
        print(f"with tor: {request.get_global_info()['ip']}")
        request.close()
        
        print(f"tor restart")
        Tor.restart()
        request:CatsRequest = CatsRequest(proxy=proxy)
        print(f"with tor: {request.get_global_info()['ip']}")
        print(f"with tor: {request.get_global_info()['ip']}")
        request.close()

if __name__ == "__main__":
    unittest.main()