
from bs4 import BeautifulSoup, SoupStrainer
import requests


def get_soup_by_url(url: str, ss: SoupStrainer = None) -> BeautifulSoup:
    try:
        rr = requests.get(url)
        bs = BeautifulSoup(rr.text, 'html.parser', parse_only=ss)
        return bs

    except Exception as e:
        print(e)


def get_soup_from_response(res, ss: SoupStrainer = None) -> BeautifulSoup:
    try:
        bs = BeautifulSoup(res.text, 'html.parser', parse_only=ss)
        return bs

    except Exception as e:
        print(e)


