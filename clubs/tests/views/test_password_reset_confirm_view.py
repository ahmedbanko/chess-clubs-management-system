"""Tests of the password reset confirm view."""

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from clubs.models import User


class PasswordResetConfirmViewTestCase(TestCase):
    """Unit tests of the password reset confirm view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')

    def test_get_password_reset_confirm(self):
        response = self.client.post(reverse('password_reset'),
                                    {'email': self.user.email})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        token = response.context[0]['token']
        uid = response.context[0]['uid']
        response = self.client.get(
            reverse('password_reset_confirm',
                    kwargs={
                        'token': token,
                        'uidb64': uid
                    }))
        self.assertEqual(response.status_code, 302)
