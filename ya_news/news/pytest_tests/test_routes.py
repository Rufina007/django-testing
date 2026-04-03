from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


HOME_URL = reverse('news:home')
LOGIN_URL = reverse('users:login')
SIGNUP_URL = reverse('users:signup')
LOGOUT_URL = reverse('users:logout')

pytestmark = pytest.mark.django_db


def test_logout_for_anonymous_user(client):
    response = client.post(LOGOUT_URL)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGIN_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (SIGNUP_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (
            pytest.lazy_fixture('detail_url'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK,
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND,
        ),
    )
)
def test_pages_availability(url, parametrized_client, expected_status):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url')),
)
def test_redirect_for_anonymous_client(client, url):
    expected_url = f'{LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
