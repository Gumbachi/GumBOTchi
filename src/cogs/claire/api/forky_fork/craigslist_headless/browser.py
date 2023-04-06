from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class CraigslistBrowser:
    driver = None

    def _get_options(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")

        return options

    def __init__(self):
        self.driver = webdriver.Firefox(options=self._get_options())

    def visit(self, url):
        self.driver.get(url)

    def show_source(self, wait=False):
        if wait:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#search-results-page-1 > ol > div')
                )
            )

        return self.driver.execute_script("return document.documentElement.outerHTML")

    def quit(self):
        self.driver.quit()