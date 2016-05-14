import re
from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item

from django.template.loader import render_to_string


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('home.html')

        # Um vorher den csrd token raus zu hoeln
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        observed_html = re.sub(csrf_regex, '', response.content.decode())

        self.assertEqual(observed_html, expected_html)

    def test_home_page_only_saves_items_when_necessary(self):
        request = HttpRequest()
        home_page(request)
        self.assertEqual(Item.objects.count(), 0)

    def test_home_page_can_save_a_POST_request(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['item_text'] = 'A new list Item'

        response = home_page(request)

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list Item')

    def test_home_page_redirects_after_POST(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['item_text'] = 'A new list Item'

        response = home_page(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_home_page_displays_all_list_items(self):
        Item.objects.create(text='itmem1')
        Item.objects.create(text='itmem2')

        request = HttpRequest()
        response = home_page(request)

        self.assertIn('itmem1', response.content.decode())
        self.assertIn('itmem2', response.content.decode())


        """
         #  observed_html = re.sub(csrf_regex, '', response.content.decode())
         #  AttributeError: 'NoneType' object has no attribute 'content'


         #Um vorher den csrd token raus zu hoeln
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        observed_html = re.sub(csrf_regex, '', response.content.decode())

        # test_string = response.content.decode()
        text_file_response = open("test_response.log", "w")
        text_file_response.write(observed_html)
        text_file_response.close()

        self.assertIn('A new list Item', response.content.decode())

        expected_html = render_to_string('home.html', {'new_item_text': 'A new list Item'})

        text_file_expected = open("test_expeceted.log", "w")
        text_file_expected.write(expected_html)
        text_file_expected.close()

        self.assertEqual(observed_html, expected_html)


        """


# TODO more test


class ItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self):
        first_item = Item()
        first_item.text = 'the first (ever) list item'
        first_item.save()

        second_item = Item()
        second_item.text = 'second list item'
        second_item.save()

        saved_items =Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'the first (ever) list item')
        self.assertEqual(second_saved_item.text, 'second list item')