import logging
import requests
from requests import Session
import json
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from abc import ABCMeta, abstractmethod

class CatsRequestSessionError(RuntimeError):
    pass

class CatsRequestSession:
    def __init__(self):
        """[summary]
        """
        self.session = requests.Session()

    def close(self):
        """[summary]
        """
        self.session.close()

    def get_cookie(self, key):
        return self.session.cookies.get(key)

    def get_cookies(self):
        return self.session.cookies.get_dict()
    
    def _mk_result(self, ret, response_content_type):
        if response_content_type == "html":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return (ret.headers, soup)
        elif response_content_type == "json":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return (ret.headers, json.loads(str(soup)))
        else:
            return (ret.headers, ret.content)
        
    def _check_status_code(self, url, status_code):
        if status_code != 200:
            raise CatsRequestSessionError(f"{url} response code is {status_code}")
        return True
        
    def get(self, url, response_content_type=None, proxy=None):
        """[summary]
        
        Arguments:
            url {[type]} -- [description]
        
        Keyword Arguments:
            response_content_type {[type]} -- [html or json] (default: {None})
            proxy {[type]} -- [description] (default: {None})
        
        Raises:
            RuntimeError: [description]
        
        Returns:
            [type] -- [description]
        """
        if proxy:
            ret = self.session.get(url, proxies= self.burpProxies, verify=False)
        else:
            ret = self.session.get(url)
        self._check_status_code(url, ret.status_code)
        return self._mk_result(ret, response_content_type)

    def post(self, url, post_data, response_content_type, proxy=None):
        if proxy:
            ret = self.session.post(url, post_data, proxies=self.burpProxies, verify=False)
        else:
            ret = self.session.post(url, post_data)
        self._check_status_code(url, ret.status_code)
        return self._mk_result(ret, response_content_type)

"""[summary]
"""
class CatsWebDriverSession:
    def __init__(self, binary_location, executable_path, proxy, headless):
        """[summary]
        
        Arguments:
            binary_location {[type]} -- [description]
            executable_path {[type]} -- [description]
            proxy {[type]} -- [description]
            headless {[type]} -- [description]
        """
        options = Options()
        options.binary_location = binary_location
        logging.info(f"WebDriverSession.__init__ : {binary_location}, {executable_path}, {proxy}, {headless}")
        if headless:
            options.add_argument('--headless')
            # https://www.ytyng.com/blog/ubuntu-chromedriver/
            options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
            options.add_argument("start-maximized") # open Browser in maximized mode
            options.add_argument("disable-infobars") # disabling infobars
            options.add_argument("--disable-extensions") # disabling extensions
            options.add_argument("--disable-gpu") # applicable to windows os only
            options.add_argument("--no-sandbox") # Bypass OS security model
        if proxy:
            logging.info("WebDriverSession proxy on")
            options.add_argument(f"proxy-server={proxy}")
        self.driver = webdriver.Chrome(options=options, executable_path=executable_path)

    def close(self):
        """[close WebDriverSession]
        """
        self.driver.quit()

    def get_cookies(self):
            return self.driver.get_cookies()

    def to_request_session(self) -> CatsRequestSession: 
        """[summary]
        
        Returns:
            CatsRequestSession -- [description]
        """
        session = CatsRequestSession()
        for cookie in self.driver.get_cookies():
            self.driver.cookies.set(cookie["name"], cookie["value"])
        return session

    def wait_rendering_by_id(self, id, timeout=20):
        """[summary]
        
        Arguments:
            id {[type]} -- [description]
        
        Keyword Arguments:
            timeout {int} -- [description] (default: {20})
        """
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.ID, id)))

    def wait_rendering_by_class(self, _class, timeout=20):
        """[summary]
        
        Arguments:
            _class {[type]} -- [description]
        
        Keyword Arguments:
            timeout {int} -- [description] (default: {20})
        """
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, _class)))

    def html(self):
        html = self.driver.page_source.encode('utf-8')
        return BeautifulSoup(html, "lxml")

    def reload(self):
        self.driver.refresh()