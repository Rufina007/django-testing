from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый текст комментария'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    initial_count = Comment.objects.count()
    client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == initial_count


def test_user_can_create_comment(
        author_client, author, news, detail_url):
    initial_count = Comment.objects.count()
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == initial_count + 1
    comment = Comment.objects.get(text=FORM_DATA['text'])
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    initial_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert Comment.objects.count() == initial_count
    assertFormError(response.context['form'], 'text', errors=WARNING)


def test_author_can_delete_comment(
        author_client, comment, delete_url, detail_url):
    initial_count = Comment.objects.count()
    response = author_client.post(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == initial_count - 1


def test_user_cant_delete_comment_of_another_user(
        reader_client, comment, delete_url):
    initial_count = Comment.objects.count()
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count


def test_author_can_edit_comment(
        author_client, comment, edit_url, detail_url):
    response = author_client.post(edit_url, data=FORM_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
        reader_client, comment, edit_url):
    response = reader_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news
