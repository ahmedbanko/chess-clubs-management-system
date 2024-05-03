"""Tests of the update match output form."""

from django.test import TestCase
from clubs.forms import UpdateMatchOutcomeForm
from clubs.models import Match, User, Club, Application, Membership
import pytz
import datetime


class CreateMatchTestCase(TestCase):
    """Unit test of the update match output form."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.utc = pytz.UTC
        self.club = Club.objects.get(name='PolecatChess')
        self.player1 = User.objects.get(username='johndoe')
        self.player2 = User.objects.get(username='janedoe')
        self.player1application = self._create_application(self.player1)
        self.player2application = self._create_application(self.player2)
        self.membership1 = self._create_membership(self.player1,
                                                   Membership.OFFICER)
        self.membership2 = self._create_membership(self.player2,
                                                   Membership.MEMBER)
        self.match = Match.objects.create(
            player_1=self.player1,
            player_2=self.player2,
            club=self.club,
            location='Bush House',
            date_time=self.utc.localize(datetime.datetime(2022, 9, 25, 10,
                                                          30)),
            status=Match.PENDING,
            id=1)
        self.form_input = {'status': Match.DRAW}

    def test_form_has_necessary_fields(self):
        form = UpdateMatchOutcomeForm()
        self.assertIn('status', form.fields)

    def test_form_accepts_valid_input(self):
        form = UpdateMatchOutcomeForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_status(self):
        self.form_input['status'] = None
        form = UpdateMatchOutcomeForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_non_status(self):
        self.form_input['status'] = "NotAStatusChoice"
        form = UpdateMatchOutcomeForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_update_match_outcome_does_not_create_new_match(self):
        form = UpdateMatchOutcomeForm(data=self.form_input)
        before_count = Match.objects.count()
        form.save(self.match.id)
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count)

    def test_update_match_outcome_does_saves_new_match_outcome(self):
        form = UpdateMatchOutcomeForm(data=self.form_input)
        form.save(self.match.id)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.DRAW)

    def _create_application(self, user):
        return Application.objects.create(
            user=user,
            club=self.club,
            personal_statement="personal statement",
            status=Application.ACCEPTED)

    def _create_membership(self, user, role):
        return Membership.objects.create(user=user, club=self.club, role=role)
