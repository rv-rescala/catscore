import unittest
from catscore.http.web_driver import CatsWebDriver
import argparse
import time
from catscore.lib.functional import calc_time

class TestCatsWebDriver(unittest.TestCase):
    binary_location = "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
    executable_path = "/Users/rv/workspace/docker/finance_db/tools/chromedriver"
    proxy = None
    headless = True
    
    def test_simple_get(self):
        """[python -m unittest tests.http.test_web_driver.TestCatsWebDriver.test_simple_get]
        """
        request:CatsRequest = CatsWebDriver(binary_location=self.binary_location, executable_path=self.executable_path, proxy=self.proxy, headless=self.headless)
        html = request.move(url="https://yahoo.co.jp")
        time.sleep(10)
        request.close()
        
    @calc_time()
    def cal_log_time(self, request):
        return request.log


    def test_websocket(self):
        """[python -m unittest tests.http.test_web_driver.TestCatsWebDriver.test_websocket]
        """
        request:CatsRequest = CatsWebDriver(binary_location=self.binary_location, executable_path=self.executable_path, proxy=self.proxy, headless=self.headless)
        html = request.move(url="https://demo.click-sec.com/ixop/order.do")
        time.sleep(2)
        log = self.cal_log_time(request)
        with open("/Users/rv/Desktop/a.text", mode='w') as f:
            for l in log:
                f.write(l)
        request.close()

if __name__ == "__main__":
    unittest.main()