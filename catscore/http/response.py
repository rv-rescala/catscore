from dataclasses import dataclass
from typing import List, Mapping
from bs4 import BeautifulSoup
import json

@dataclass
class Response:
    """[summary]
    """
    headers: Mapping[str, str]
    content: str

@dataclass
class ResponseHtml:
    """[summary]
    """
    headers: Mapping[str, str]
    content: BeautifulSoup

@dataclass
class ResponseJson:
    """[summary]
    """
    headers: Mapping[str, str]
    content:  json