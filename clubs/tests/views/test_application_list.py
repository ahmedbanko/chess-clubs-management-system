"""Tests of the application list view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Application, User, Club
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next

class ApplicationsViewTestCase(TestCase, MenuTesterMixin):
    """Tests of the application list view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.url = reverse('applications')
        self.user = User.objects.get(username='johndoe')

    def test_application_list_url(self):
        self.assertEqual(self.url, '/applications/')

    def test_get_application_list(self):
        self.client.login(email=self.user.email, password='Password123')
        club = Club.objects.get(name='PolecatChess')
        Application.objects.create(user=self.user,
                                   club=club,
                                   personal_statement="Personal Statement")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')
        self.assert_no_club_menu(response, club.id)
        applications = response.context['applications']
        self.assertEquals(len(applications), 1)

    def test_get_application_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
