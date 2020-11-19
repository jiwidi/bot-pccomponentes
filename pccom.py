import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from chromedriver_py import binary_path  # this will get you the path variable

options = Options()
options.page_load_strategy = "eager"
chrome_options = ChromeOptions()
# chrome_options.add_argument("--disable-application-cache")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

LOGIN_URL = "https://www.pccomponentes.com/login"

log = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s : %(message)s : %(levelname)s -%(name)s", datefmt="%d%m%Y %I:%M:%S %p"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.setLevel(10)
log.addHandler(handler)


class Bot:
    def __init__(self, username, password, debug=False):
        if not debug:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            executable_path=binary_path, options=options, chrome_options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)
        self.username = username
        self.password = password
        self.login()
        time.sleep(1)

    def login(self):
        self.driver.get(LOGIN_URL)
        WebDriverWait(self.driver, 2).until(
                presence_of_element_located((By.XPATH, '//*[@id="login-form"]/div[4]/div/input'))
            )
        self.driver.find_element_by_xpath('//*[@id="login-form"]/div[4]/div/input').send_keys(
            self.username + Keys.RETURN
        )
        self.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/div/div/input').send_keys(
            self.password + Keys.RETURN
        )

        log.info(f"Logged in as {self.username}")

    def run_item(self, item_url, price_limit=1500, delay=5):
        log.info(f"Loading page: {item_url}")
        self.driver.get(item_url)
        try:
            product_title = self.wait.until(
                presence_of_element_located((By.XPATH, "article-availability"))
            )
            log.info(f"Loaded page for {product_title.text}")
        except:
            log.error(self.driver.current_url)
        WebDriverWait(self.driver, 5).until(
                presence_of_element_located((By.XPATH, '//*[@id="btnsWishAddBuy"]/button[3]'))
            )
        availability = self.driver.find_element_by_xpath(
            '//*[@id="btnsWishAddBuy"]/button[3]'
        ).text.replace("\n", " ")

        price = WebDriverWait(self.driver, 5).until(
                presence_of_element_located((By.ID, 'precio-main'))
            )
        price = float(price.text.replace("€","").replace(",","."))
        log.info(f"Initial availability message is: {availability}")
        while not availability=="Comprar" or price > price_limit:
            self.driver.refresh()
            log.info("Refreshing page.")
            WebDriverWait(self.driver, 5).until(
                presence_of_element_located((By.XPATH, '//*[@id="btnsWishAddBuy"]/button[3]'))
            )
            availability = self.driver.find_element_by_xpath(
            '//*[@id="btnsWishAddBuy"]/button[3]'
            ).text.replace("\n", " ")
            price = WebDriverWait(self.driver, 5).until(
                presence_of_element_located((By.ID, 'precio-main'))
            )
            price = float(price.text.replace("€","").replace(",","."))
            log.info(f"Current availability message is: {availability} at {price} eur")
            time.sleep(delay)

        log.info("Item in stock, buy now button found!")
        log.info(f"Attempting to buy item")
        self.buy_now()


    def buy_now(self):
        #Start buying
        self.driver.find_element_by_xpath(
            '//*[@id="btnsWishAddBuy"]/button[3]'
        ).click()
        #Start order
        WebDriverWait(self.driver, 5).until(
                presence_of_element_located((By.ID, 'GTM-carrito-realizarPedidoPaso1'))
            ).click()
        time.sleep(1)
        #Wait for order details
        WebDriverWait(self.driver, 5).until(
                presence_of_element_located((By.XPATH, '//*[@id="ticket-pago"]/p/label/span'))
            )
        time.sleep(1)
        status_pay = WebDriverWait(self.driver, 5).until(
                presence_of_element_located((By.ID, 'GTM-carrito-finalizarCompra'))
            )

        while not status_pay.text=="PAGAR Y FINALIZAR":
            time.sleep(0.1)
        self.driver.find_element_by_xpath('//*[@id="ticket-pago"]/p/label').click()
        log.info("Clicking 'Buy Now'.")

        try:
            place_order = WebDriverWait(self.driver, 2).until(
                presence_of_element_located((By.ID, "GTM-carrito-finalizarCompra"))
            )
        except:
            log.debug("Fail while buying product")
        log.info("Clicking 'Place Your Order'.")
        place_order.click()