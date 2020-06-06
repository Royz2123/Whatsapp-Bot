import selenium

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

import DB_API


class WhatsappClient:
    TEST_CONTACT = "אלון שראל תלפיות"
    TEST_CONTACT = "אלון בויאנג'ו - 39"
    TEST_CONTACT = "רון סנה שלום"
    TEST_CONTACT = "רזיאל גרצמן המלך"


    # TEST_CONTACT = "אשר תלפיות"
    # TEST_CONTACT = "דניאל הר אבן תלפיות"
    # TEST_CONTACT = "אסף תלפיות"
    # TEST_CONTACT = "אסף היי ניסיון"

    def __init__(self, show_scan=True):
        # scan modes
        self.show_scan = show_scan
        self.play_scan = False
        self.init_scan = False
        self.kill_scan = False

    def set_window(self):
        if not self.show_scan:
            self._driver.set_window_position(-2000, 0)
        else:
            self._driver.set_window_position(0, 0)
        self._driver.set_window_size(1024, 768)

    def initialize(self, initialize=True):
        options = webdriver.ChromeOptions()

        # if not minimize:
        options.add_argument(r"user-data-dir=./user_data")

        self._driver = webdriver.Chrome(
            executable_path="./drivers/chromedriver5.exe",
            chrome_options=options
        )

        self.set_window()

        # get the whatsapp window
        self._driver.get("https://web.whatsapp.com")

        # wait until page loads?
        # if prompt:
        #     input("Scan QR Code, And then Enter")
        #     print("Logged in")
        # else:
        #     time.sleep(20)

        if initialize:
            DB_API.init_db(DB_API.TEST_NAMES, DB_API.TEST_HOURS)

    def get_scan_mode(self):
        return self.play_scan, self.show_scan

    def close_conn(self):
        self._driver.quit()

    def scan_users(self, user_lst=DB_API.TEST_NAMES):
        try:
            for contact_name in user_lst:
                # wait until need to play scan
                while not self.play_scan:
                    time.sleep(0.5)
                    self.set_window()

                    if self.kill_scan:
                        break

                self.set_window()
                if self.kill_scan:
                    break

                self.get_contact_time(contact_name)
                DB_API.set_image(contact_name, self.get_contact_image(contact_name, True))
        except Exception as e:
            print(f"Scan failed")

    def open_contact(self, contact=TEST_CONTACT):
        contact_names = contact.split(" ")
        last_index = len(contact_names)
        found = False

        while not found and last_index != 0:
            contact_name = " ".join(contact_names[:last_index])
            print(f"Searching for {contact_name}")

            try:
                inp_xpath_search = "//div[@class='_3FRCZ copyable-text selectable-text']"
                input_box_search = self._driver.find_element_by_xpath(inp_xpath_search)
                input_box_search.click()
                input_box_search.clear()
                input_box_search.send_keys(contact_name)

                time.sleep(0.5)

                # inp_xpath_contact = "//div[@class='_3j7s9']"
                selected_contact = self._driver.find_element_by_xpath(
                    '//span[starts-with(@title, "' + contact_name + '")]'
                )
                selected_contact.click()

                found = True
                break
            except Exception as e:
                print(f"Could not find contact name: {contact_name}")
                # print(e)

            last_index -= 1

        if last_index != 0:
            print(f"Found contact: {contact_name}")
        else:
            print("Couldn't find contact at all")

    def write_message(self, message="this is a test"):
        self.open_contact()

        inp_xpath = '//div[@class="_2S1VP copyable-text selectable-text"][@contenteditable="true"][@data-tab="1"]'
        input_box = self._driver.find_element_by_xpath(inp_xpath)
        time.sleep(1)
        input_box.send_keys(message + Keys.ENTER)
        time.sleep(1)

    def get_contact_image(self, contact_name, opened=False):
        if not opened:
            self.open_contact(contact_name)

        image_xpath = "//header[@class='_1iFv8']//div[@class='m7liR']//div[@class='_1BjNO']//img[@class='_2goTk _1Jdop _3Whw5']"
        # image_xpath = "//header[@class='_2y17h']"
        image_url = ""
        try:
            image_url = self._driver.find_elements_by_xpath(image_xpath)[-1].get_attribute("src")
            print(f"Found image for {contact_name}: {image_url}")
        except Exception as e:
            # print("#############################")
            # print(e)
            # print("#############################")
            print(f"Couldn't find image for {contact_name}")
            image_url = "default user"
        return image_url

    def get_contact_time(self, contact_name):
        self.open_contact(contact_name)

        try:
            header_xpath = "//span[@class='_3-cMa _3Whw5']"

            while True:
                time.sleep(0.5)
                header_text = self._driver.find_element_by_xpath(header_xpath).text

                if header_text == "click here for contact info":
                    time.sleep(0.5)
                else:
                    break

            if header_text.startswith("last seen"):
                last_seen = header_text.split("last seen ")[1]

                DB_API.lastseen_update(contact_name, last_seen)
                DB_API.not_online_now(contact_name)  # is needed?

                print("Last seen: ", contact_name, " ", last_seen)
            elif header_text.startswith("online") or header_text.startswith("typing"):
                DB_API.online_now(contact_name)

                print("Online user: ", contact_name)
            else:
                raise selenium.common.exceptions.NoSuchElementException("Uknown header")

        except selenium.common.exceptions.NoSuchElementException as e:
            print("User not online, disabled last seen")
            # print(e)
            DB_API.not_online_now(contact_name)
