import logging
import requests
from requests import Session
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from abc import ABCMeta, abstractmethod

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

    def get(self, url, response_content_type=None, proxy=None):
        if proxy:
            ret = self.session.get(url, proxies= self.burpProxies, verify=False)
        else:
            ret = self.session.get(url)
        if ret.status_code != 200:
            raise RuntimeError(f"{url} response code is {ret.status_code}")
        if response_content_type == "html":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return (ret.headers, soup)
        else:
            return (ret.headers, ret.content)

    def post(self, url, post_data, response_content_type, proxy=None):
        if proxy:
            ret = self.session.post(url, post_data, proxies=self.burpProxies, verify=False)
        else:
            ret = self.session.post(url, post_data)
        if ret.status_code != 200:
            raise RuntimeError(f"{url} response code is {ret.status_code}")
        if response_content_type == "html":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return (ret.headers, soup)
        else:
            return (ret.headers, ret.content)

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