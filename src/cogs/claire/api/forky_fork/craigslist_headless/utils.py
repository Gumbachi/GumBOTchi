from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib.parse import urlencode
from .browser import CraigslistBrowser

ALL_SITES_URL = 'https://www.craigslist.org/about/sites'
SITE_URL = 'https://%s.craigslist.org'
USER_AGENT = 'Mozilla/5.0'

def bs(content):
    return BeautifulSoup(content, 'html.parser')

def isiterable(var):
    try:
        return iter(var) and True
    except TypeError:
        return False

def requests_get(*args, **kwargs):
    """
    Retries if a RequestException is raised (could be a connection error or
    a timeout).
    """
    logger = kwargs.pop('logger', None)
    wait = kwargs.pop('wait', False)
    # Set default User-Agent header if not defined.
    # kwargs.setdefault('headers', {}).setdefault('User-Agent', USER_AGENT)
    if kwargs:
        query_string = urlencode(kwargs["params"])
        url = args[0] + "?" + query_string
    else:
        url = args[0]

    try:
        CraigslistBrowser.visit(url)
        src = CraigslistBrowser.show_source(wait)
        return src
    except Exception as e:
        print(f"Failed getting source: {url}")
        return None
