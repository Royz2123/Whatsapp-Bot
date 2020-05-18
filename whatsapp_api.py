import selenium

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time


class WhatsappClient():
    TEST_CONTACT = "אלון שראל תלפיות"
    TEST_CONTACT = "אלון בויאנג'ו - 39"
    TEST_CONTACT = "רון סנה רפאל"
    TEST_CONTACT = "רזיאל גרצמן תלפיות"
    TEST_CONTACT = "אשר תלפיות"
    TEST_CONTACT = "דניאל הר אבן תלפיות"
    TEST_CONTACT = "אסף תלפיות"

    def __init__(self, need_qr=False):
        options = webdriver.ChromeOptions()
        options.add_argument(r"user-data-dir=./user_data")

        self._driver = webdriver.Chrome(
            executable_path="./drivers/chromedriver4.exe",
            chrome_options=options
        )
        self._driver.get("https://web.whatsapp.com")

        if need_qr:
            input("Scan QR Code, And then Enter")
            print("Logged in")
        else:
            time.sleep(20)

    def close_conn(self):
        self._driver.quit()

    def open_contact(self, contact=TEST_CONTACT):
        inp_xpath_search = "//div[@class='_2S1VP copyable-text selectable-text']"
        input_box_search = self._driver.find_element_by_xpath(inp_xpath_search)
        input_box_search.click()
        input_box_search.send_keys(WhatsappClient.TEST_CONTACT)

        time.sleep(1)

        selected_contact = self._driver.find_element_by_xpath("//span[@title='" + contact + "']")
        selected_contact.click()

    def write_message(self, message="this is a test"):
        self.open_contact()

        inp_xpath = '//div[@class="_2S1VP copyable-text selectable-text"][@contenteditable="true"][@data-tab="1"]'
        input_box = self._driver.find_element_by_xpath(inp_xpath)
        time.sleep(1)
        input_box.send_keys(message + Keys.ENTER)
        time.sleep(1)
        self._driver.quit()

    def get_contact_image(self):
        self.open_contact()

        image_xpath = "//img[@class='Qgzj8 gqwaM _3FXB1']"
        image_url = self._driver.find_elements_by_xpath(image_xpath)[1].get_attribute("src")

        print(image_url)

    def get_contact_time(self):
        self.open_contact()

        try:
            header_xpath = "//span[@class='O90ur _3FXB1']"

            while True:
                header_text = self._driver.find_element_by_xpath(header_xpath).text

                if header_text == "click here for contact info":
                    time.sleep(1)
                else:
                    break

            last_seen = "not found"
            if header_text.startswith("last seen"):
                last_seen = header_text.split("last seen ")[1]
                print("Last time he was seen: ", last_seen)
            else:
                print(header_text)

        except selenium.common.exceptions.NoSuchElementException as e:
            print("User not online, disabled last seen")
            print(e)
