import re
from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item, List

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


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = 'the first (ever) list item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'second list item'
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'the first (ever) list item')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'second list item')
        self.assertEqual(second_saved_item.list, list_)


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
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post('/lists/%d/add_item' % (correct_list.id,), data={
            'item_text': 'A new item for existing list'
        })

        self.assertEqual(List.objects.count(), 2)
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post('/lists/%d/add_item' % (correct_list.id,), data={
            'item_text': 'A new item for existing list'
        })

        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))
