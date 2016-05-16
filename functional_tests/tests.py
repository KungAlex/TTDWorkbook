from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    # eigene Helper Methode
    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows], "New to-do item not found in your list")

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.live_server_url)
        self.assertIn('To-Do', self.browser.title)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # Inputbox finden
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'), 'Enter a to-do item')

        # 1. itme anlegen
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        list_url=self.browser.current_url
        self.assertRegex(list_url, '/lists/.+')
        self.check_for_row_in_list_table('1: Buy peacock feathers')

        # 2. Item anlegen
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('was anderes')
        inputbox.send_keys(Keys.ENTER)

        self.check_for_row_in_list_table('1: Buy peacock feathers')
        self.check_for_row_in_list_table('2: was anderes')

        # new user
        self.browser.quit()
        self.browser =webdriver.Firefox()
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)

        # new Item
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Milch')
        inputbox.send_keys(Keys.ENTER)

        new_list_url = self.browser.current_url
        self.assertRegex( new_list_url, '/lists/.+')
        self.assertNotEqual(new_list_url, list_url)

        # again
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Milch', page_text)

        # reminder self.fail('Finish the test!')

    def test_layout_andstyling(self):
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] / 2, 512, delta=5)

        inputbox.send_keys('testing\n')

        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] / 2, 512, delta=5)

