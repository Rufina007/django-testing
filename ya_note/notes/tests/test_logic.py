from http import HTTPStatus

from pytils.translit import slugify
from notes.forms import WARNING
from notes.models import Note

from .base import BaseTestCase


FORM_DATA = {
    'title': 'Новый заголовок',
    'text': 'Новый текст',
    'slug': 'new-slug',
}


class TestNoteCreation(BaseTestCase):

    def test_anonymous_user_cant_create_note(self):
        initial_count = Note.objects.count()
        self.client.post(self.add_url, data=FORM_DATA)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url, data=FORM_DATA)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, FORM_DATA['title'])
        self.assertEqual(note.text, FORM_DATA['text'])
        self.assertEqual(note.author, self.author)

    def test_not_unique_slug(self):
        initial_count = Note.objects.count()
        form_data = {**FORM_DATA, 'slug': self.note.slug}
        response = self.author_client.post(self.add_url, data=form_data)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertFormError(
            response.context['form'],
            field='slug',
            errors=(self.note.slug + WARNING)
        )

    def test_empty_slug(self):
        Note.objects.all().delete()
        form_data = {'title': FORM_DATA['title'], 'text': FORM_DATA['text']}
        response = self.author_client.post(self.add_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(form_data['title']))


class TestNoteEditDelete(BaseTestCase):

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.edit_url, data=FORM_DATA
        )
        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, FORM_DATA['title'])
        self.assertEqual(updated_note.text, FORM_DATA['text'])
        self.assertEqual(updated_note.slug, FORM_DATA['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(
            self.edit_url, data=FORM_DATA
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.note.author)

    def test_author_can_delete_note(self):
        initial_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_other_user_cant_delete_note(self):
        initial_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
