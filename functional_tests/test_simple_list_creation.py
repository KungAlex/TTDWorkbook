from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(FunctionalTest):
    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.server_url)
        self.assertIn('To-Do', self.browser.title)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # Inputbox finden
        inputbox = self.get_item_input_box()
        self.assertEqual(inputbox.get_attribute('placeholder'), 'Enter a to-do item')

        # 1. itme anlegen
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        list_url = self.browser.current_url
        self.assertRegex(list_url, '/lists/.+')
        self.check_for_row_in_list_table('1: Buy peacock feathers')

        # 2. Item anlegen
        inputbox = self.get_item_input_box()
        inputbox.send_keys('was anderes')
        inputbox.send_keys(Keys.ENTER)

        self.check_for_row_in_list_table('1: Buy peacock feathers')
        self.check_for_row_in_list_table('2: was anderes')

        # new user
        self.browser.quit()
        self.browser = webdriver.Firefox()
        self.browser.get(self.server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)

        # new Item
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Milch')
        inputbox.send_keys(Keys.ENTER)

        new_list_url = self.browser.current_url
        self.assertRegex(new_list_url, '/lists/.+')
        self.assertNotEqual(new_list_url, list_url)

        # again
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Milch', page_text)

        # reminder self.fail('Finish the test!')

