from selenium import webdriver
import unittest


class AuthorizationMixin:
    def login(self):
        # The first new customer of the day has just arrived. We start by taking down their
        # information in our on-line system

        # The fitter goes to the home page of Slowfit app:
        self.browser.get('http://localhost:8000')

        # Notices page title. He's in the right spot
        self.assertIn('Slowfit', self.browser.title)

        # Because the Slowfit app hold confidential customer information, he has to
        # log in first. He clicks the link offering to get him to the login screen:
        try:
            login_link = self.browser.find_element_by_id("LoginLink")
        except Exception as e:
            self.fail("Could not find login link")
        login_link.click()

        # He is presented with a login screen:
        self.assertIn('Login', self.browser.title)
        try:
            username = self.browser.find_element_by_name("username")
        except Exception as e:
            self.fail("Could not find username input")

        try:
            password = self.browser.find_element_by_name("password")
        except Exception as e:
            self.fail("Could not find password input")

        username.send_keys("jan")
        password.send_keys("wbw417")

        try:
            submit_button = self.browser.find_element_by_id("SubmitLogin")
        except Exception as e:
            self.fail("Could not find submit button")

        submit_button.click()


class LoginTest(unittest.TestCase, AuthorizationMixin):
    def setUp(self) -> None:
        options = webdriver.ChromeOptions()
        options.binary_location = "C:/Program Files (x86)/Google/Chrome Beta/Application/chrome.exe"
        self.browser = webdriver.Chrome(options=options)

    def tearDown(self) -> None:
        self.browser.quit()

    def test_login(self):
        self.login()


class NewCustomerTest(unittest.TestCase, AuthorizationMixin):
    def setUp(self) -> None:
        options = webdriver.ChromeOptions()
        options.binary_location = "C:/Program Files (x86)/Google/Chrome Beta/Application/chrome.exe"
        self.browser = webdriver.Chrome(options=options)
        self.login()

    def tearDown(self) -> None:
        self.browser.quit()

    def test_customer_list(self):
        # He clicks the 'Customers' link get to the list of customers:
        try:
            customers_link = self.browser.find_element_by_id("Customers")
        except:
            self.fail("Could not find Customers link")
        self.fail("END")


if __name__ == '__main__':
    unittest.main(warnings='ignore')