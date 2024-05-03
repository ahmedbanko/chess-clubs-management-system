"""Tests of the forfeit match view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Match, Club, User, Application, Membership
from clubs.tests.helpers import reverse_with_next
import pytz
import datetime


class ForfeitMatchViewTestCase(TestCase):
    """Unit tests of the forfeit match view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/other_clubs.json',
    ]

    def setUp(self):
        self.utc = pytz.UTC
        self.club = Club.objects.get(name='PolecatChess')
        self.player1 = User.objects.get(username='johndoe')
        self.player2 = User.objects.get(username='janedoe')
        self.player3 = User.objects.get(username='petrapickles')
        self.player1application = self._create_application(self.player1)
        self.player2application = self._create_application(self.player2)
        self.player3application = self._create_application(self.player3)
        self.membership1 = self._create_membership(self.player1,
                                                   Membership.OFFICER)
        self.membership2 = self._create_membership(self.player2,
                                                   Membership.MEMBER)
        self.membership3 = self._create_membership(self.player3,
                                                   Membership.MEMBER)
        self.match = Match.objects.create(
            player_1=self.player1,
            player_2=self.player2,
            club=self.club,
            location='Bush House',
            date_time=self.utc.localize(datetime.datetime(2024, 9, 25, 10,
                                                          30)),
            status=Match.PENDING,
            id=1)
        self.url = reverse('forfeit_match',
                           kwargs={
                               'club_id': self.club.id,
                               'match_id': self.match.id
                           })

    def test_forfeit_match_url(self):
        self.assertEqual(
            self.url, '/club/' + str(self.club.id) + '/forfeit_match/' +
            str(self.match.id))

    def test_get_forfeit_match(self):
        self.client.login(email=self.player1.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')

    def test_get_forfeit_match_with_player_2(self):
        self.client.login(email=self.player2.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')

    def test_get_forfeit_match_form_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_post_forfeit_match_when_not_logged_in(self):
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse_with_next('log_in', self.url)
        before_count = Match.objects.count()
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PENDING)

    def test_forfeit_match_before_it_is_played(self):
        self.client.login(email=self.player1.email, password='Password123')
        before_count = Match.objects.count()
        response = self.client.get(self.url, follow=True)
        self.match.refresh_from_db()
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(self.match.status, Match.PLAYER2)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')

    def test_forfeit_match_after_it_is_played(self):
        self.client.login(email=self.player1.email, password='Password123')
        self.match.date_time = self.utc.localize(
            datetime.datetime(2024, 9, 25, 10, 30))
        before_count = Match.objects.count()
        response = self.client.get(self.url, follow=True)
        self.match.refresh_from_db()
        after_count = Match.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(self.match.status, Match.PLAYER2)
        self.assertEqual(
            self.match.date_time,
            self.utc.localize(datetime.datetime(2024, 9, 25, 10, 30)))
        self.assertTemplateUsed(response, 'home_templates/club_home.html')

    def test_forfeit_match_with_not_authorised_member(self):
        self.client.login(email=self.player3.email, password='Password123')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PENDING)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')

    def test_forfeit_match_with_outcome(self):
        self.client.login(email=self.player2.email, password='Password123')
        self.match.status = Match.PLAYER1
        self.match.save()
        response = self.client.get(self.url, follow=True)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PLAYER1)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_forfeit_nonexisting_match(self):
        self.client.login(email=self.player1.email, password='Password123')
        url = reverse('forfeit_match',
                      kwargs={
                          'club_id': self.club.id,
                          'match_id': 1000
                      })
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PENDING)

    def test_forfeit_match_from_different_club(self):
        self.client.login(email=self.player1.email, password='Password123')
        self._create_second_match_from_different_club()
        url = reverse('forfeit_match',
                      kwargs={
                          'club_id': self.club.id,
                          'match_id': 2
                      })
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.match.refresh_from_db()
        self.different_match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PENDING)
        self.assertEqual(self.different_match.status, Match.PENDING)

    def _create_second_match_from_different_club(self):
        self.different_club = Club.objects.get(name='PolecatChess_2')
        self.different_player1 = User.objects.get(username='petrapickles')
        self.different_player2 = User.objects.get(username='janedoe')
        self.different_player1application = Application.objects.create(
            user=self.different_player1,
            club=self.different_club,
            personal_statement="Player1 personal statement",
            status=Application.ACCEPTED)

        self.different_player2application = Application.objects.create(
            user=self.different_player2,
            club=self.different_club,
            personal_statement="Player2 personal statement",
            status=Application.ACCEPTED)
        self.different_membership1 = Membership.objects.create(
            user=self.different_player1,
            club=self.different_club,
            role=Membership.MEMBER)
        self.different_membership2 = Membership.objects.create(
            user=self.different_player2,
            club=self.different_club,
            role=Membership.MEMBER)
        self.different_match = Match.objects.create(
            player_1=self.different_player1,
            player_2=self.different_player2,
            club=self.different_club,
            location='Bush House',
            date_time=self.utc.localize(datetime.datetime(2020, 9, 25, 10,
                                                          30)),
            status=Match.PENDING,
            id=2)

    def _create_application(self, user):
        return Application.objects.create(
            user=user,
            club=self.club,
            personal_statement="personal statement",
            status=Application.ACCEPTED)

    def _create_membership(self, user, role):
        return Membership.objects.create(user=user, club=self.club, role=role)
