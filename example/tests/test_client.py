import time

from selenium import webdriver

from django.conf import settings
from django.test import LiveServerTestCase


class FrontendTestCase(LiveServerTestCase):
    fixtures = ['fixtures/content.yaml',]

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()
        super().tearDown()

    def test_pages_navigation(self):
        # user navigates to site homepage
        self.browser.get(self.live_server_url)
        # user sees the proper page title
        self.assertIn('MiniCMS Example Project', self.browser.title)
        # user sees the homepage contents
        main_content_element = self.browser.find_element_by_id('main_container')
        self.assertIn('This is the content of the homepage', main_content_element.text)
        # user clicks contact page link
        contact_link = self.browser.find_element_by_id('contact_link')
        contact_link.click()
        # user notices URL change
        new_url = self.browser.current_url
        self.assertEqual(new_url, '/content/contact/')
        # user sees the proper page title
        self.assertIn('MiniCMS Example Project | Contact', self.browser.title)
        # user sees the homepage contents
        main_content_element = self.browser.find_element_by_id('main_container')
        self.assertIn('This is a page with some contact information', main_content_element.text)
