"""Tests of the create match form."""

import datetime
from django.test import TestCase
from django import forms
import pytz
from clubs.forms import CreateMatchForm
from clubs.models import Match, User, Club, Application, Membership


class CreateMatchTestCase(TestCase):
    """ Unit test of the create match form."""
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.utc = pytz.UTC
        self.user1 = User.objects.get(username='johndoe')
        self.user2 = User.objects.get(username='petrapickles')
        self.user3 = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='PolecatChess')
        self.match_time = self.utc.localize(
            datetime.datetime(2022, 9, 25, 10, 30))
        self.match_location = 'Bush House'
        self.usr1application = self._create_application(self.user1)
        self.usr2application = self._create_application(self.user2)
        self.usr3application = self._create_application(self.user3)
        self.membership1 = self._create_membership(self.user1)
        self.membership2 = self._create_membership(self.user2)
        self.membership3 = self._create_membership(self.user3)
        self.form_input = {
            'player_1': self.user1,
            'player_2': self.user2,
            'location': self.match_location,
            'date_time': self.match_time
        }

    def test_form_has_necessary_fields(self):
        form = CreateMatchForm(self.club)
        self.assertIn('player_1', form.fields)
        self.assertIn('player_1', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('date_time', form.fields)
        date_time_field = form.fields['date_time']
        self.assertTrue(isinstance(date_time_field.widget,
                                   forms.DateTimeInput))

    def test_form_accepts_valid_input(self):
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_player_1(self):
        self.form_input['player_1'] = None
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_player_2(self):
        self.form_input['player_2'] = None
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_location(self):
        self.form_input['location'] = ''
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_date_time(self):
        self.form_input['date_time'] = ''
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_identical_players(self):
        self.form_input['player_1'] = self.user1
        self.form_input['player_2'] = self.user1
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_old_date(self):
        self.form_input['date_time'] = self.utc.localize(
            datetime.datetime(2000, 9, 25, 10, 30))
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_alphabet_input_for_datetime(self):
        self.form_input['date_time'] = "wrong datetime input"
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertTrue(form.is_invalid_date())

    def test_form_rejects_conflicting_matches(self):
        Match.objects.create(player_1=self.user1,
                             player_2=self.user2,
                             club=self.club,
                             location=self.match_location,
                             date_time=self.match_time)

        self.form_input['player_2'] = self.user3
        form = CreateMatchForm(club=self.club, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_match_must_save(self):
        form = CreateMatchForm(club=self.club, data=self.form_input)
        before_count = Match.objects.count()
        form.save(self.club)
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count + 1)

    def _create_application(self, user):
        return Application.objects.create(
            user=user,
            club=self.club,
            personal_statement="personal statement",
            status=Application.ACCEPTED)

    def _create_membership(self, user):
        return Membership.objects.create(user=user,
                                         club=self.club,
                                         role=Membership.MEMBER)
