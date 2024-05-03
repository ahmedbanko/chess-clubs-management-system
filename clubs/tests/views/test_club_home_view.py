"""Tests of the club home view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next


class ClubHomeViewTestCase(TestCase, MenuTesterMixin):
    """Unit tests of the club home view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='PolecatChess')
        self.url = reverse('club_home', kwargs={'club_id': self.club.id})

    def test_club_home_url(self):
        self.assertEqual(self.url, '/club/' + str(self.club.id))

    def test_get_club_home(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user, club=self.club)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        self.assert_member_menu(response, self.club.id)
        url = reverse('leave_club', kwargs={'club_id': self.club.id})
        with self.assertHTML(response, f'a[href="{url}"]'):
            pass
        url = reverse('delete_club', kwargs={'club_id': self.club.id})
        self.assertNotHTML(response, f'a[href="{url}"]')
        member.delete()

    def test_get_club_home_redirects_without_permissions(self):
        self.client.login(email=self.user.email, password='Password123')
        redirect_url = reverse('applications')
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_club_home_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_club_home_as_owner_shows_delete_option(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.OWNER)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        self.assert_officer_menu(response, self.club.id)
        url = reverse('delete_club', kwargs={'club_id': self.club.id})
        with self.assertHTML(response, f'a[href="{url}"]'):
            pass
        url = reverse('leave_club', kwargs={'club_id': self.club.id})
        self.assertNotHTML(response, f'a[href="{url}"]')
        member.delete()