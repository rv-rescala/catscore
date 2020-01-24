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
    def __init__(self):
        """[summary]
        """
        self.session = requests.Session()

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

    def _mk_result(self, ret, response_content_type):
        if response_content_type == "html":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return ResponseHtml(ret.headers, soup)
        elif response_content_type == "json":
            soup = BeautifulSoup(ret.content, features="html.parser")
            return ResponseJson(ret.headers, json.loads(str(soup)))
        else:
            return Response(ret.headers, ret.content)

    def _check_status_code(self, url, status_code):
        if status_code != 200:
            raise CatsRequestSessionError(f"{url} response code is {status_code}")
        return True

    def retry_get(self, url, response_content_type=None, proxy=None, retry_num=4, wait=1):
        reponse = None
        for i in range(retry_num):
            try:
                reponse = self.get(url, response_content_type, proxy)
                return reponse
            except Exception:
                print(f"retry_get: {url} retry {i}")
                time.sleep(wait)
        raise CatsRequestSessionError(f"{url} retry count is {retry_num}")

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
    
    def download(self, url:str, fullpath:str, request_type:str = "get", post_data=None, proxy=None):
        if request_type == "post":
            bi = self.post(url=url, post_data=post_data, proxy=proxy)
        else:
            bi = self.get(url=url, proxy=proxy).content
        with open(fullpath, "wb") as f:
            f.write(bi)
        
        