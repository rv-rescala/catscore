from catscore.lib.logger import CatsLogging as logging
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
from catscore.http.error import CatsRequestSessionError
from catscore.http.response import Response, ResponseHtml, ResponseJson
import time
from asgiref.sync import sync_to_async
import asyncio
import aiohttp

class CatsRequest:
    DEFAULT_TOR_PROXY = {'http':'socks5://127.0.0.1:9050','https':'socks5://127.0.0.1:9050'}
    DEFAULT_TIMEOUT = (10.0, 20.0)
    
    def __init__(self, proxy=None, verify=True, timeout=None):
        """[summary]
        """
        self.session = requests.Session()
        self.proxy = proxy
        self.verify = verify
        if timeout:
            self.timeout = timeout
        else:
            self.timeout = self.DEFAULT_TIMEOUT

    @classmethod
    def create_instance_from_json(cls, json_path:str):
        with open(json_path, "r") as f:
            j = json.load(f)
            proxy = None
            try:
                http_proxy = j["web_driver"]["http_proxy"]
                https_proxy = j["web_driver"]["https_proxy"]
                proxy = {"http": http_proxy, "https": https_proxy}
            except Exception:
                print("proxy is None")
            d = CatsRequest(proxy=proxy)
        return d
    
    def __enter__(self):
        """[summary]
        
        Returns:
            [type] -- [description]
        """
        return self

    def __exit__(self, ex_type, ex_value, trace):
        """[summary]
        
        Arguments:
            ex_type {[type]} -- [description]
            ex_value {[type]} -- [description]
            trace {[type]} -- [description]
        """
        self.close()
        
    def close(self):
        """[summary]
        """
        self.session.close()

    def get_cookie(self, key):
        return self.session.cookies.get(key)

    def get_cookies(self):
        return self.session.cookies.get_dict()

    def _mk_result(self, ret, response_content_type: str):
        if response_content_type == "html":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return ResponseHtml(ret.headers, soup, ret)
        elif response_content_type == "json":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return ResponseJson(ret.headers, json.loads(str(soup)), ret)
        else:
            return Response(ret.headers, ret.content, ret)

    def _check_status_code(self, url, status_code):
        if status_code != 200:
            raise CatsRequestSessionError(f"{url} response code is {status_code}")
        return True

    def retry_get(self, url, response_content_type=None, retry_num=4, wait=1):
        reponse = None
        for i in range(retry_num):
            try:
                reponse = self.get(url, response_content_type)
                return reponse
            except Exception:
                print(f"retry_get: {url} retry {i}")
                time.sleep(wait)
        raise CatsRequestSessionError(f"{url} retry count is {retry_num}")

    def get(self, url, response_content_type=None):
        """[summary]
        
        Arguments:
            url {[type]} -- [description]
        
        Keyword Arguments:
            response_content_type {[type]} -- [html or json] (default: {None})
        
        Raises:
            RuntimeError: [description]
        
        Returns:
            [type] -- [description]
        """
        if self.proxy:
            ret = self.session.get(url, proxies= self.proxy, verify=self.verify, timeout=self.timeout)
        else:
            ret = self.session.get(url, timeout=self.timeout)
        self._check_status_code(url, ret.status_code)
        return self._mk_result(ret, response_content_type)

    def post(self, url, post_data, response_content_type):
        if self.proxy:
            ret = self.session.post(url, post_data, proxies=self.proxy, verify=self.verify, timeout=self.timeout)
        else:
            ret = self.session.post(url, post_data, timeout=self.timeout)
        self._check_status_code(url, ret.status_code)
        return self._mk_result(ret, response_content_type)

    def download(self, url:str, fullpath:str, request_type:str = "get", post_data=None):
        if request_type == "post":
            bi = self.post(url=url, post_data=post_data)
        else:
            bi = self.get(url=url, proxy=proxy).content
        with open(fullpath, "wb") as f:
            f.write(bi)

    def get_global_info(self):
        url = "https://ipinfo.io"
        return self.get(url=url, response_content_type="json").content