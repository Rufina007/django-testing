from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        client, form_data, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, author, form_data, news, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client, comment, comment_id_for_args, news_id_for_args):
    url = reverse('news:delete', args=comment_id_for_args)
    news_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url)
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        reader_client, comment, comment_id_for_args):
    url = reverse('news:delete', args=comment_id_for_args)
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client, comment, comment_id_for_args,
        news_id_for_args, form_data):
    url = reverse('news:edit', args=comment_id_for_args)
    news_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        reader_client, comment, comment_id_for_args, form_data):
    url = reverse('news:edit', args=comment_id_for_args)
    original_text = comment.text
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
