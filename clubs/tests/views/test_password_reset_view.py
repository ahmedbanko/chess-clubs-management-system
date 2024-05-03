"""Tests of the password reset view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User


class PasswordResetViewTestCase(TestCase):
    """Unit tests of the password reset view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('password_reset')
        self.user = User.objects.get(username='johndoe')

    def test_password_reset_url(self):
        self.assertEqual(self.url, '/password_reset/')

    def test_post_password_reset(self):
        response = self.client.post(reverse('password_reset'),
                                    {'email': self.user.email})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('password_reset.html')
