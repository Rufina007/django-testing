from http import HTTPStatus

from .base import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_pages_availability_get(self):
        cases = (
            (self.home_url, self.client, HTTPStatus.OK),
            (self.login_url, self.client, HTTPStatus.OK),
            (self.signup_url, self.client, HTTPStatus.OK),
            (self.list_url, self.author_client, HTTPStatus.OK),
            (self.add_url, self.author_client, HTTPStatus.OK),
            (self.success_url, self.author_client, HTTPStatus.OK),
            (self.detail_url, self.author_client, HTTPStatus.OK),
            (self.edit_url, self.author_client, HTTPStatus.OK),
            (self.delete_url, self.author_client, HTTPStatus.OK),
            (self.detail_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.edit_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.delete_url, self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for url, test_client, status in cases:
            with self.subTest(url=url):
                response = test_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_logout_post(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.list_url,
            self.add_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
