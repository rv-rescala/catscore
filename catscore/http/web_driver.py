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
from catscore.http.request import CatsRequest
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class CatsWebDriver:
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
            
        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance': 'INFO'}
        self.driver = webdriver.Chrome(options=options, executable_path=executable_path,desired_capabilities=caps)
        self.driver.implicitly_wait(5)

    def close(self):
        """[Close WebDriverSession, if chromewebdriver dosen't kill, plsease execute "killall chromedriver"]
        
        """
        self.driver.quit()

    def reload(self):
        self.driver.refresh()

    @property
    def cookies(self):
            return self.driver.get_cookies()

    def to_request_session(self) -> CatsRequest: 
        """[summary]
        
        Returns:
            CatsRequest -- [description]
        """
        session = CatsRequest()
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

    def move(self, url):
        self.driver.get(url)

    @property
    def html(self):
        html = self.driver.page_source.encode('utf-8')
        return BeautifulSoup(html, "lxml")

    @property
    def log(self):
        result = []
        for entry in self.driver.get_log('performance'):
            result.append(entry['message'])
        return result
