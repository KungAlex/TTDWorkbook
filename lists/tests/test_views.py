import re
from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item, List

from django.template.loader import render_to_string
from django.utils.html import escape


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


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_.id,))
        self.assertTemplateUsed(response, 'list.html')

    def test_display_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itmem1', list=correct_list)
        Item.objects.create(text='itmem2', list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='other itmem1', list=other_list)
        Item.objects.create(text='other itmem2', list=other_list)

        response = self.client.get('/lists/%d/' % (correct_list.id,))

        text_file_expected = open("list_view.log", "w")
        text_file_expected.write(response.content.decode())
        text_file_expected.close()

        ## dont work
        # self.assertContains('itmem1', response.content.decode())
        # self.assertContains('itmem2', response.content.decode())

        self.assertNotIn('other itmem1', response.content.decode())
        self.assertNotIn('other itmem2', response.content.decode())

        self.assertIn('itmem1', response.content.decode())
        self.assertIn('itmem2', response.content.decode())

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get('/lists/%d/' % (correct_list.id,))
        self.assertEqual(response.context['list'], correct_list)

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post('/lists/%d/' % (correct_list.id,), data={
            'item_text': 'A new item for existing list'
        })

        self.assertEqual(List.objects.count(), 2)
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_lists_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post('/lists/%d/' % (correct_list.id,), data={
            'item_text': 'A new item for existing list'
        })

        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))

    def test_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()

        response = self.client.post('/lists/%d/' % (list_.id,), data={
            'item_text': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        expected_error = escape("You can't have an empty list item")
        self.assertIn(expected_error, response.content.decode())


class NewListTest(TestCase):
    def test_saving_a_POST_request(self):
        self.client.post('/lists/new', data={'item_text': 'A new list Item'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list Item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list Item'})
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/%d/' % (new_list.id,))
        ## ist das selbe wie
        # self.assertEqual(response.status_code, 302)
        # self.assertEqual(response['location'], '/lists/the-only-list/')


class NewItemTest(TestCase):

    def test_validation_errory_are_sent_nack_to_home_page_template(self):
        response = self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = escape("You can't have an empty list item")
        self.assertIn(expected_error, response.content.decode())

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
