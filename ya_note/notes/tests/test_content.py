from notes.forms import NoteForm

from .base import BaseTestCase


class TestNotesList(BaseTestCase):

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_note_not_in_list_for_another_user(self):
        response = self.reader_client.get(self.list_url)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_create_note_page_contains_form(self):
        response = self.author_client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_page_contains_form(self):
        response = self.author_client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
