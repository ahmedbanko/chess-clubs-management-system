"""Tests of the new application form."""

from django.test import TestCase
from clubs.models import User, Club
from clubs.models import Application
from clubs.forms import ApplicationForm


class ApplicationFormTestCase(TestCase):
    """Unit test of the new application form."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='PolecatChess')

    def test_valid_application_form(self):
        input = {'personal_statement': 'x' * 200, 'club': self.club}
        form = ApplicationForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_application_form(self):
        input = {'personal_statement': 'x' * 600, 'club': self.club}
        form = ApplicationForm(data=input)
        self.assertFalse(form.is_valid())

    def test_application_must_save(self):
        input = {'personal_statement': 'Hi!', 'club': self.club}
        form = ApplicationForm(data=input)
        before_count = Application.objects.count()
        form.save(self.user)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        application = Application.objects.get(user=self.user)
        self.assertEqual(application.personal_statement, 'Hi!')