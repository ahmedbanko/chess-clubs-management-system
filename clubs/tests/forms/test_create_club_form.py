"""Tests of the create club form."""

from django.test import TestCase
from clubs.forms import CreateClubForm
from clubs.models import Club


class CreateClubFormTestCase(TestCase):
    """Unit tests of the create club form."""

    fixtures = ['clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.form_input = {
            'name': 'PolecatChess2',
            'location': 'London',
            'description': 'Welcome to Polecat chess club!'
        }

    def test_valid_create_club_form(self):
        form = CreateClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)

    def test_form_must_save_correctly(self):
        form = CreateClubForm(data=self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        club = Club.objects.get(name='PolecatChess')
        self.assertEqual(club.location, 'London')
        self.assertEqual(club.description, 'Welcome to Polecat chess club!')