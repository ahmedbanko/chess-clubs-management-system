"""Tests of the password reset done view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User


class PasswordResetDoneViewTestCase(TestCase):
    """Unit tests of the password reset done view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('password_reset_done')
        self.user_one = User.objects.get(username='johndoe')
        self.user_two = User.objects.get(username='janedoe')

    def test_password_reset_url(self):
        self.assertEqual(self.url, '/password_reset/done/')

    def test_get_password_reset_done(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response,
                                'account_templates/password_reset_done.html')
