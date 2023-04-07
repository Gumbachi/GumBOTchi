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
        page_source = CraigslistBrowser.show_source(wait)
        return page_source
        
    except RequestException as exc:
        if logger:
            logger.warning('Request failed (%s). Retrying ...', exc)
        CraigslistBrowser.visit(url)
        return CraigslistBrowser.show_source(wait)
    except Exception as e:
            print(e)
            return None

def get_list_filters(url):
    list_filters = {}
    page_source = requests_get(url)
    soup = bs(page_source)
    for list_filter in soup.find_all('div', class_='search-attribute'):
        filter_key = list_filter.attrs['data-attr']
        filter_labels = list_filter.find_all('label')
        options = {opt.text.strip(): opt.find('input').get('value')
                   for opt in filter_labels}
        list_filters[filter_key] = {'url_key': filter_key, 'value': options}
    return list_filters
