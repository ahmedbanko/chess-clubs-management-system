"""Tests of the close account view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next


class CloseAccountViewTestCase(TestCase):
    """Unit tests of the close account view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json'
        ]

    def setUp(self):
        self.url = reverse('close_account')
        self.user_one = User.objects.get(username='johndoe')

    def test_close_account_url(self):
        self.assertEqual(self.url, '/close_account/')

    def test_get_close_account_url(self):
        self.client.login(email=self.user_one.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'account_templates/close_account.html')

    def test_get_close_account_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_close_account_redirects_when_owner_of_a_club(self):
        self.client.login(email=self.user_one.email, password='Password123')
        club = Club.objects.get(name='PolecatChess')
        membership = Membership.objects.create(user=self.user_one, 
                                               club=club, 
                                               role=Membership.OWNER)
        redirect_url = reverse('dashboard')
        response = self.client.get(self.url)
        self.assertRedirects(response,
                            redirect_url, 
                            status_code=302, 
                            target_status_code=200)

    def test_successful_account_close(self):
        self.client.login(email=self.user_one.email, password='Password123')
        user_count_before = User.objects.count()
        response = self.client.post(self.url, follow=True)
        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, user_count_before - 1)
        response_url = reverse('home')
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        self.assertTemplateUsed(response, 'account_templates/home.html')
