"""Tests of the user match list view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Match, Club, Application, Membership
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next
import pytz
import datetime


class ClubListTest(TestCase, MenuTesterMixin):
    """Unit tests of the user match list view."""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('user_matches')
        self.utc = pytz.UTC
        self.user1 = User.objects.get(username='johndoe')
        self.user2 = User.objects.get(username='petrapickles')
        self.club = Club.objects.get(name='PolecatChess')
        self.match_time = self.utc.localize(
            datetime.datetime(2022, 9, 25, 14, 40))
        self.usr1application = Application.objects.create(
            user=self.user1,
            club=self.club,
            personal_statement="User1 personal statement",
            status=Application.ACCEPTED)
        self.usr2application = Application.objects.create(
            user=self.user2,
            club=self.club,
            personal_statement="User2 personal statement",
            status=Application.ACCEPTED)

        self.membership1 = Membership.objects.create(user=self.user1,
                                                     club=self.club,
                                                     role=Membership.MEMBER)
        self.membership2 = Membership.objects.create(user=self.user2,
                                                     club=self.club,
                                                     role=Membership.MEMBER)

        self.match1 = Match.objects.create(
            player_1=self.user1,
            player_2=self.user2,
            club=self.club,
            location="Bush House floor 6",
            date_time=self.match_time,
            status=Match.PENDING,
        )

        self.match2 = Match.objects.create(
            player_1=self.user1,
            player_2=self.user2,
            club=self.club,
            location="Bush House floor 7",
            date_time=self.utc.localize(datetime.datetime(2020, 9, 18, 13,
                                                          00)),
            status=Match.PLAYER1)

    def test_match_list_url(self):
        self.assertEqual(self.url, '/my_matches/')

    def test_get_match_list(self):
        self.client.login(email=self.user1.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'match_templates/user_matches.html')
        self.assert_logged_in_menu(response)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Petra Pickles')
        self.assertContains(response, 'Bush House floor 6')

    def test_get_match_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
