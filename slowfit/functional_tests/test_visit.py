from datetime import date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import SlowfitTestCase
from ..models.fits import Customer, Visit
from ..testdata import visit as data, customer as customer_data


class VisitTest(SlowfitTestCase):
    def setUp(self) -> None:
        super(VisitTest, self).setUp()
        self.customer_id = customer_data.create_customer()

    def test_visit_list(self):
        # He clicks the 'Customers' link get to the list of customers:
        customers_link = self.find_menu_item("Customers")
        customers_link.click()
        customer_details_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, customer_data.CUSTOMER_LAST_NAME)
        customer_details_link.click()
        visits_tab = self.browser.find_element(By.ID, "visits-tab")
        visits_tab.click()
        # self.assertCountEqual()


    def test_create_new_customer(self):
        customers_link = self.find_menu_item("Customers")
        customers_link.click()
        new_customer_button = self.browser.find_element_by_id("new_customer_link")
        new_customer_button.click()
        input_element = self.browser.find_element_by_name("firstName")
        while input_element.tag_name != "button":
            name = input_element.get_attribute("name")
            value = customer_data.CUSTOMER_DATA[name]
            input_element.send_keys(value)
            input_element.send_keys(Keys.TAB)
            input_element = self.browser.switch_to.active_element
        input_element.click()

        # Wait for the 'view customer' page and check that insert worked:
        element = self.browser.find_element(By.ID, "email")
        self.assertEqual(element.text.strip(), customer_data.CUSTOMER_EMAIL)

    def test_edit_customer(self):
        customer = Customer.objects.create(**customer_data.CUSTOMER_DATA)
        customers_link = self.find_menu_item("Customers")
        customers_link.click()
        customer_details_link = self.browser.find_element_by_id(f"firstName-link-{customer.id}")
        customer_details_link.click()

        customer_edit_button = self.browser.find_element_by_id("customer-edit-link")
        customer_edit_button.click()

        input_element = self.browser.find_element_by_name("email")
        input_element.send_keys(Keys.CONTROL + "a")
        input_element.send_keys(customer_data.CUSTOMER_EMAIL_2)
        submit_form = self.browser.find_element_by_id("submit_form_button")
        submit_form.click()

        # Wait for the 'view customer' page and check that the update stuck
        element = self.browser.find_element(By.ID, "email")
        self.assertEqual(element.text.strip(), customer_data.CUSTOMER_EMAIL_2)
