"""Tests of the create match view."""

import datetime
from django.test import TestCase
from django.urls import reverse
import pytz
from clubs.forms import CreateMatchForm
from clubs.models import Club, User, Application, Match
from clubs.models import Membership
from clubs.tests.helpers import LogInTester, MenuTesterMixin, reverse_with_next


class CreateClubViewTestCase(TestCase, LogInTester, MenuTesterMixin):
    """Unit tests of the create match view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json'
    ]

    def setUp(self):
        self.utc = pytz.UTC
        self.user1 = User.objects.get(username='johndoe')
        self.user2 = User.objects.get(username='petrapickles')
        self.club = Club.objects.get(name='PolecatChess')
        self.url = reverse('create_match', kwargs={'club_id': self.club.id})
        self.match_time = self.utc.localize(
            datetime.datetime(2022, 9, 25, 14, 40))
        self.usr1application = self._create_application(self.user1)
        self.usr2application = self._create_application(self.user2)
        self.membership1 = self._create_membership(self.user1,
                                                   Membership.OFFICER)
        self.membership2 = self._create_membership(self.user2,
                                                   Membership.MEMBER)
        Match.objects.all().delete()
        self.form_input = {
            'player_1': self.user1.id,
            'player_2': self.user2.id,
            'location': 'Bush House',
            'date_time': self.match_time
        }

    def test_create_match_url(self):
        self.assertEqual(self.url,
                         '/club/' + str(self.club.id) + '/create_match')

    def test_get_create_match(self):
        self.client.login(email=self.user1.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/create_match.html')
        form = response.context['form']
        self.assertFalse(form.is_bound)
        self.assert_officer_menu(response, self.club.id)

    def test_get_create_match_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_create_match_should_reject_old_date(self):
        self.client.login(email=self.user1.email, password='Password123')
        self.form_input['date_time'] = self.utc.localize(
            datetime.datetime(2000, 9, 25, 10, 30))
        before_count = Match.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/create_match.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateMatchForm))
        self.assertTrue(form.is_bound)

    def test_create_match_should_reject_alphabet_input_for_datetime(self):
        self.client.login(email=self.user1.email, password='Password123')
        self.form_input['date_time'] = "wrong datetime input"
        before_count = Match.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/create_match.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateMatchForm))
        self.assertTrue(form.is_bound)

    def test_get_create_match_with_not_authorised_member(self):
        self.client.login(email=self.user2.email, password='Password123')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_unsuccesful_create_match(self):
        self.client.login(email=self.user1.email, password='Password123')
        self.form_input['player_1'] = ''
        before_count = Match.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/create_match.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateMatchForm))
        self.assertTrue(form.is_bound)

    def test_succesful_create_match(self):
        self.client.login(email=self.user1.email, password='Password123')
        before_count = Match.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count + 1)

    def _create_application(self, user):
        return Application.objects.create(
            user=user,
            club=self.club,
            personal_statement="personal statement",
            status=Application.ACCEPTED)

    def _create_membership(self, user, role):
        return Membership.objects.create(user=user, club=self.club, role=role)
