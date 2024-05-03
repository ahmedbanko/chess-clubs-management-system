"""Tests of the update match view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Match, Club, User, Application, Membership
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next
import pytz
import datetime


class UpdateMatchViewTestCase(TestCase, MenuTesterMixin):
    """Unit tests of the update match view."""

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
        self.player1application = Application.objects.create(
            user=self.player1,
            club=self.club,
            personal_statement="Player1 personal statement",
            status=Application.ACCEPTED)
        self.player2application = Application.objects.create(
            user=self.player2,
            club=self.club,
            personal_statement="Player2 personal statement",
            status=Application.ACCEPTED)
        self.membership1 = Membership.objects.create(user=self.player1,
                                                     club=self.club,
                                                     role=Membership.OFFICER)
        self.membership2 = Membership.objects.create(user=self.player2,
                                                     club=self.club,
                                                     role=Membership.MEMBER)
        self.match = Match.objects.create(
            player_1=self.player1,
            player_2=self.player2,
            club=self.club,
            location='Bush House',
            date_time=self.utc.localize(datetime.datetime(2020, 9, 25, 10,
                                                          30)),
            status=Match.PENDING,
            id=1)
        self.form_input = {'status': Match.DRAW}
        self.url = reverse('update_match',
                           kwargs={
                               'club_id': self.club.id,
                               'match_id': self.match.id
                           })

    def test_update_match_url(self):
        self.assertEqual(
            self.url, '/club/' + str(self.club.id) + '/update_match/' +
                      str(self.match.id))

    def test_get_update_match(self):
        self.client.login(email=self.player1.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'club_templates/update_match.html')
        self.assert_officer_menu(response, self.club.id)
        self.assertEqual(response.status_code, 200)

    def test_get_update_match_form_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assert_no_menu(response)

    def test_post_update_match_form_when_not_logged_in(self):
        response = self.client.post(self.url, self.form_input, follow=True)
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

    def test_get_update_match_with_not_authorised_member(self):
        self.client.login(email=self.player2.email, password='Password123')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PENDING)

    def test_post_update_match_with_not_authorised_member(self):
        self.client.login(email=self.player2.email, password='Password123')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PENDING)

    def test_successful_update_match(self):
        self.client.login(email=self.player1.email, password='Password123')
        self.assertEqual(self.match.is_overdue(), True)
        before_count = Match.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        after_count = Match.objects.count()
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.DRAW)
        self.assertEqual(after_count, before_count)

    def test_unsuccessful_update_match(self):
        self.client.login(email=self.player1.email, password='Password123')
        before_count = Match.objects.count()
        self.form_input['status'] = 'RandomBadStatus'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTemplateUsed(response, 'club_templates/update_match.html')
        self.assertEqual(response.status_code, 200)
        after_count = Match.objects.count()
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PENDING)
        self.assertEqual(after_count, before_count)

    def test_cannot_update_match_that_has_not_been_played_yet(self):
        self.client.login(email=self.player1.email, password='Password123')
        before_count = Match.objects.count()
        self.match.date_time = self.utc.localize(
            datetime.datetime(2024, 9, 25, 10, 30))
        self.assertEqual(self.match.is_overdue(), False)
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        after_count = Match.objects.count()
        self.assertEqual(self.match.status, Match.PENDING)
        self.assertEqual(after_count, before_count)
        self.assertEqual(
            self.match.date_time,
            self.utc.localize(datetime.datetime(2024, 9, 25, 10, 30)))

    def test_cannot_update_match_that_has_been_updated(self):
        self.client.login(email=self.player1.email, password='Password123')
        before_count = Match.objects.count()
        self.match.status = Match.PLAYER1
        self.match.save()
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        after_count = Match.objects.count()
        self.assertEqual(self.match.status, Match.PLAYER1)
        self.assertEqual(after_count, before_count)

    def test_get_update_nonexisting_match(self):
        self.client.login(email=self.player1.email, password='Password123')
        url = reverse('update_match',
                      kwargs={
                          'club_id': self.club.id,
                          'match_id': 1000
                      })
        response = self.client.get(url, follow=True)
        response_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.PENDING)

    def test_get_update_match_from_different_club(self):
        self.client.login(email=self.player1.email, password='Password123')
        self._create_second_match_from_different_club()
        url = reverse('update_match',
                      kwargs={
                          'club_id': self.club.id,
                          'match_id': 2
                      })
        response = self.client.get(url, follow=True)
        response_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
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
