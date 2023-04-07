import time
import threading
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class CraigslistBrowser:
    OPTIONS = Options()
    OPTIONS.add_argument('--headless')
    OPTIONS.add_argument("--no-sandbox")
    OPTIONS.add_argument("--disable-gpu")
    OPTIONS.add_argument("--disable-infobars")
    OPTIONS.add_argument("--disable-extensions")
    OPTIONS.add_argument("--disable-dev-shm-usage")
    OPTIONS.add_argument('--disable-application-cache')
    OPTIONS.add_argument("--disable-setuid-sandbox")

    DRIVER = None
    last_called = time.time()
    waiting = False

    @classmethod
    def set_driver(cls):
        cls.DRIVER = webdriver.Chrome(options=cls.OPTIONS)

    @classmethod
    def visit(cls, url):
        cls.last_called = time.time()
        if not cls.DRIVER:
            cls.set_driver()
        
        cls.DRIVER.get(url)

    @classmethod
    def show_source(cls, wait=False):
        if wait:
            cls.waiting = True
            WebDriverWait(cls.DRIVER, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#search-results-page-1 > ol > div')
                )
            )
            
        data = cls.DRIVER.execute_script("return document.documentElement.outerHTML")

        cls.waiting = False
        return data

    @classmethod
    def quit(cls):
        if not cls.DRIVER:
            return
                
        cls.DRIVER.quit()
        cls.DRIVER = None

    @classmethod
    def check_activity(cls):
        if (time.time() - cls.last_called >= 5) and not cls.waiting:
            cls.quit()
        threading.Timer(5, cls.check_activity).start()