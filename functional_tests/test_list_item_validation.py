from unittest import skip
from .base import FunctionalTest


class ItemValidationTest(FunctionalTest):

    def test_cannot_add_empty_lists_items(self):
        # submit an empty item
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('\n')

        # there is an error massage
        error = self.browser.find_element_by_css_selector('.has-error')
        self.assertEqual(error.text, "You can't have an empty list item")

        # add a not emtpy item
        self.get_item_input_box().send_keys('Milch\n')
        self.check_for_row_in_list_table('1: Milch')

        # submit an empty item
        self.get_item_input_box().send_keys('\n')

        # there is an error massage on the list page
        self.check_for_row_in_list_table('1: Milch')
        error = self.browser.find_element_by_css_selector('.has-error')
        self.assertEqual(error.text, "You can't have an empty list item")

        # And She can correct them
        self.get_item_input_box().send_keys('Tee\n')
        self.check_for_row_in_list_table('1: Milch')
        self.check_for_row_in_list_table('2: Tee')

        # self.fail('write me!')

    def test_cannot_add_duplicate_items(self):
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('Buy wellies\n')
        self.check_for_row_in_list_table('1: Buy wellies')

        # tries to enter a duplicate
        self.get_item_input_box().send_keys('Buy wellies\n')
        self.check_for_row_in_list_table('1: Buy wellies')
        error = self.browser.find_element_by_css_selector('.has-error')
        self.assertEqual(error.text, "you've already got this in your list")
