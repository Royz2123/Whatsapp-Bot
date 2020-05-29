import selenium

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

import DB_API


class WhatsappClient():
    TEST_CONTACT = "אלון שראל תלפיות"
    TEST_CONTACT = "אלון בויאנג'ו - 39"  # TODO: Special Characters
    TEST_CONTACT = "רון סנה שלום"
    TEST_CONTACT = "רזיאל גרצמן המלך"
    # TEST_CONTACT = "אשר תלפיות"
    # TEST_CONTACT = "דניאל הר אבן תלפיות"
    # TEST_CONTACT = "אסף תלפיות"
    # TEST_CONTACT = "אסף היי ניסיון"

    def __init__(self, minimize=False):
        options = webdriver.ChromeOptions()

        if not minimize:
            options.add_argument(r"user-data-dir=./user_data")

        self._driver = webdriver.Chrome(
            executable_path="./drivers/chromedriver5.exe",
            chrome_options=options
        )

        if minimize:
            self._driver.minimize_window()
            self._driver.get("https://web.whatsapp.com")

            input("Scan QR Code, And then Enter")
            print("Logged in")
        else:
            self._driver.get("https://web.whatsapp.com")
            time.sleep(20)

        DB_API.init_db(DB_API.TEST_NAMES, DB_API.TEST_HOURS)

    def close_conn(self):
        self._driver.quit()

    def scan_users(self, user_lst=DB_API.TEST_NAMES):
        for contact_name in user_lst:
            self.get_contact_time(contact_name)
            DB_API.set_image(contact_name, self.get_contact_image(contact_name))

    def open_contact(self, contact=TEST_CONTACT):
        contact_names = contact.split(" ")
        last_index = len(contact_names)
        found = False

        while not found and last_index != 0:
            print(last_index)
            contact_name = " ".join(contact_names[:last_index])
            print(f"Searching for {contact_name}")

            try:
                inp_xpath_search = "//div[@class='_2S1VP copyable-text selectable-text']"
                input_box_search = self._driver.find_element_by_xpath(inp_xpath_search)
                input_box_search.click()
                input_box_search.clear()
                input_box_search.send_keys(contact_name)

                time.sleep(1)

                # inp_xpath_contact = "//div[@class='_3j7s9']"
                selected_contact = self._driver.find_element_by_xpath(
                    "//span[starts-with(@title, '" + contact_name + "')]"
                )
                selected_contact.click()

                found = True
                break
            except Exception as e:
                print(f"Could not find contact name: {contact_name}")
                print(e)

            last_index -= 1

        if last_index != 0:
            print(f"Found contact: {contact_name}")
        else:
            print("Couldn't find contact...")

    def write_message(self, message="this is a test"):
        self.open_contact()

        inp_xpath = '//div[@class="_2S1VP copyable-text selectable-text"][@contenteditable="true"][@data-tab="1"]'
        input_box = self._driver.find_element_by_xpath(inp_xpath)
        time.sleep(1)
        input_box.send_keys(message + Keys.ENTER)
        time.sleep(1)

    def get_contact_image(self, contact_name):
        self.open_contact(contact_name)

        image_xpath = "//img[@class='Qgzj8 gqwaM _3FXB1']"
        image_url = self._driver.find_elements_by_xpath(image_xpath)[-1].get_attribute("src")

        print(image_url)
        return image_url

    def get_contact_time(self, contact_name):
        self.open_contact(contact_name)

        try:
            header_xpath = "//span[@class='O90ur _3FXB1']"

            while True:
                time.sleep(1)
                header_text = self._driver.find_element_by_xpath(header_xpath).text

                if header_text == "click here for contact info":
                    time.sleep(1)
                else:
                    break

            if header_text.startswith("last seen"):
                last_seen = header_text.split("last seen ")[1]

                DB_API.lastseen_update(contact_name, last_seen)
                DB_API.not_online_now(contact_name)     # is needed?

                print("Last seen: ", contact_name, " ", last_seen)
            elif header_text.startswith("online"):
                DB_API.online_now(contact_name)

                print("Online user: ", contact_name)
            else:
                raise selenium.common.exceptions.NoSuchElementException("Uknown header")

        except selenium.common.exceptions.NoSuchElementException as e:
            print("User not online, disabled last seen")
            print(e)
            DB_API.not_online_now(contact_name)

