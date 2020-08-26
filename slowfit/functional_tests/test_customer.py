from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import SlowfitTestCase
from ..models.fits import Customer

CUSTOMER_FIRST_NAME = "Testy"
CUSTOMER_LAST_NAME = "McTestface"
CUSTOMER_ADDRESS = "42, Test Terrace\nTestville, ON, T5T 7S7"
CUSTOMER_EMAIL = "testy.mctestface@test.com"
CUSTOMER_EMAIL_2 = "testy.mctestface_2@test.com"
CUSTOMER_PHONE_MAIN = "(555) 555-0001"
CUSTOMER_PHONE_ALT = "(555) 555-0002"
CUSTOMER_DATE_OF_BIRTH = "2000-07-13"
CUSTOMER_HEIGHT = "180"
CUSTOMER_INSEAM = "80"

CUSTOMER_FORM_DATA = {
    "firstName":  CUSTOMER_FIRST_NAME,
    "lastName":  CUSTOMER_LAST_NAME,
    "address":  CUSTOMER_ADDRESS,
    "email":  CUSTOMER_EMAIL,
    "phoneMain":  CUSTOMER_PHONE_MAIN,
    "phoneAlt":  CUSTOMER_PHONE_ALT,
    "dateOfBirth":  CUSTOMER_DATE_OF_BIRTH,
    "height":  CUSTOMER_HEIGHT,
    "inseam":  CUSTOMER_INSEAM,
}


class CustomerTest(SlowfitTestCase):
    def setUp(self) -> None:
        options = webdriver.ChromeOptions()
        options.binary_location = "C:/Program Files (x86)/Google/Chrome Beta/Application/chrome.exe"
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(10)
        self.login()

    def tearDown(self) -> None:
        self.browser.quit()

    def test_customer_list(self):
        # He clicks the 'Customers' link get to the list of customers:
        customers_link = self.find_menu_item("Customers")
        customers_link.click()
        self.browser.find_element_by_id("customers_header")

    def test_create_new_customer(self):
        customers_link = self.find_menu_item("Customers")
        customers_link.click()
        new_customer_button = self.browser.find_element_by_id("new_customer_link")
        new_customer_button.click()
        input_element = self.browser.find_element_by_name("firstName")
        while input_element.tag_name != "button":
            name = input_element.get_attribute("name")
            value = CUSTOMER_FORM_DATA[name]
            input_element.send_keys(value)
            input_element.send_keys(Keys.TAB)
            input_element = self.browser.switch_to.active_element
        input_element.click()

        # Wait for the 'view customer' page and check that insert worked:
        element = self.browser.find_element(By.ID, "email")
        self.assertEqual(element.text.strip(), CUSTOMER_EMAIL)

    def test_edit_customer(self):
        customer = Customer.objects.create(**CUSTOMER_FORM_DATA)
        customers_link = self.find_menu_item("Customers")
        customers_link.click()
        customer_details_link = self.browser.find_element_by_id(f"firstName-link-{customer.id}")
        customer_details_link.click()

        customer_edit_button = self.browser.find_element_by_id("customer-edit-link")
        customer_edit_button.click()

        input_element = self.browser.find_element_by_name("email")
        input_element.send_keys(Keys.CONTROL + "a")
        input_element.send_keys(CUSTOMER_EMAIL_2)
        submit_form = self.browser.find_element_by_id("submit_form_button")
        submit_form.click()

        # Wait for the 'view customer' page and check that the update stuck
        element = self.browser.find_element(By.ID, "email")
        self.assertEqual(element.text.strip(), CUSTOMER_EMAIL_2)
