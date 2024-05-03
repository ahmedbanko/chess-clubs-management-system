"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.tests.helpers import MenuTesterMixin


class HomeViewTestCase(TestCase, MenuTesterMixin):
    """Unit tests of the home view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(username='johndoe')

    def test_home_url(self):
        self.assertEqual(self.url, '/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account_templates/home.html')
        self.assert_no_menu(response)

    def test_get_home_redirects_when_logged_in(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'account_templates/dashboard.html')
        self.assert_logged_in_menu(response)
