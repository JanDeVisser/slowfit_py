from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver

USERNAME = "jan"
USER_PASSWORD = "top_secret"
USER_EMAIL = "jan@slowfit.com"


class SlowfitTestCase(StaticLiveServerTestCase):
    def __init__(self, *args, **kwargs):
        super(SlowfitTestCase, self).__init__(*args, **kwargs)
        self.browser = None

    def setUp(self) -> None:
        options = webdriver.ChromeOptions()
        options.binary_location = "C:/Program Files (x86)/Google/Chrome Beta/Application/chrome.exe"
        self.browser: webdriver = webdriver.Chrome(options=options)

    def tearDown(self) -> None:
        self.browser.refresh()
        self.browser.quit()

    def login(self):
        user = User.objects.create_user(username=USERNAME, email=USER_EMAIL, password=USER_PASSWORD)
        # The first new customer of the day has just arrived. We start by taking down their
        # information in our on-line system

        # The fitter goes to the home page of Slowfit app:
        self.browser.get(self.live_server_url)

        # Notices page title. He's in the right spot
        self.assertIn('Slowfit', self.browser.title)

        # Because the Slowfit app hold confidential customer information, he has to
        # log in first. He clicks the link offering to get him to the login screen:
        login_link = self.browser.find_element_by_id("LoginLink")
        login_link.click()

        # He is presented with a login screen:
        self.assertIn('Login', self.browser.title)
        username = self.browser.find_element_by_name("username")
        password = self.browser.find_element_by_name("password")

        username.send_keys(USERNAME)
        password.send_keys(USER_PASSWORD)

        submit_button = self.browser.find_element_by_id("SubmitLogin")
        submit_button.click()

    DEFAULT_TIMEOUT = 10

    def find_menu_item(self, menu_id):
        try:
            toggler = self.browser.find_element_by_class_name("navbar-toggler")
            toggler.click()
        except Exception as e:
            pass
        return self.browser.find_element_by_id(menu_id)
