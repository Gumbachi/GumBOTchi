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

    CraigslistBrowser.visit(url)
    return CraigslistBrowser.show_source(wait)

def get_list_filters(url):
    list_filters = {}
    page_source = requests_get(url)
    try:
        soup = bs(page_source)
        for list_filter in soup.find_all('div', class_='search-attribute'):
            filter_key = list_filter.attrs['data-attr']
            filter_labels = list_filter.find_all('label')
            options = {opt.text.strip(): opt.find('input').get('value')
                    for opt in filter_labels}
            list_filters[filter_key] = {'url_key': filter_key, 'value': options}
    except Exception as e:
        print("Filter error")
        print(type(page_source), page_source)
        print(e)

    return list_filters

def get_url(url):
    """ Gets details for url post """
    result = {}

    CraigslistBrowser.visit(url)
    source = CraigslistBrowser.show_source()
    
    if not source:
        return

    soup = BeautifulSoup(source)
    body = soup.find('section', id='postingbody')

    if not body:
        # This should only happen when the posting has been deleted by its
        # author.
        result['deleted'] = True
        return

    # We need to massage the data a little bit because it might include
    # some inner elements that we want to ignore.
    body_text = (getattr(e, 'text', e) for e in body
                    if not getattr(e, 'attrs', None))
    result['body'] = ''.join(body_text).strip()

    # Add created time (in case it's different from last updated).
    postinginfos = soup.find('div', {'class': 'postinginfos'})
    for p in postinginfos.find_all('p'):
        if 'posted' in p.text:
            time = p.find('time')
            if time:
                # This date is in ISO format. I'm removing the T literal
                # and the timezone to make it the same format as
                # 'last_updated'.
                created = time.attrs['datetime'].replace('T', ' ')
                result['created'] = created.rsplit(':', 1)[0]

    # Add images' urls.
    image_tags = soup.find_all('img')
    # If there's more than one picture, the first one will be repeated.
    image_tags = image_tags[1:] if len(image_tags) > 1 else image_tags
    images = []
    for img in image_tags:
        try:
            img_link = img['src'].replace('50x50c', '600x450')
            images.append(img_link)
        except KeyError:
            continue  # Some posts contain empty <img> tags.
    result['images'] = images

    # Add list of attributes as unparsed strings. These values are then
    # processed by `parse_attrs`, and are available to be post-processed
    # by subclasses.
    attrgroups = soup.find_all('p', {'class': 'attrgroup'})
    attrs = []
    for attrgroup in attrgroups:
        for attr in attrgroup.find_all('span'):
            attr_text = attr.text.strip()
            if attr_text:
                attrs.append(attr_text)
    result['attrs'] = attrs

    # If an address is included, add it to `address`.
    mapaddress = soup.find('div', {'class': 'mapaddress'})
    if mapaddress:
        result['address'] = mapaddress.text

    return result
