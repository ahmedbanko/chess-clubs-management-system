"""Tests of the dashboard view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next


class ClubListTest(TestCase, MenuTesterMixin):
    """Unit tests of the dashboard view."""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='PolecatChess')
        self.url = reverse('dashboard')

    def test_club_list_url(self):
        self.assertEqual(self.url, '/dashboard/')

    def test_get_club_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account_templates/dashboard.html')
        self.assert_no_club_menu(response, self.club.id)
        self.assertEqual(len(response.context['clubs']), 4)
        self.assertContains(response, 'PolecatChess')
        self.assertContains(response, 'PolecatChess_2')
        self.assertContains(response, 'PolecatChess_3')
        self.assertContains(response, 'PolecatChess_4')
        self.assertContains(response, 'London')
        self.assertContains(response, 'Berlin')

    def test_get_club_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
