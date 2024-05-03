"""Tests of the create club view."""

from django.test import TestCase
from django.urls import reverse
from clubs.forms import CreateClubForm
from clubs.models import Club, User, Membership
from clubs.tests.helpers import LogInTester, reverse_with_next


class CreateClubViewTestCase(TestCase, LogInTester):
    """Unit tests of the create club view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('create_club')
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'name': 'PolecatChess2',
            'location': 'London',
            'description': 'Welcome to Polecat chess club!'
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club/')

    def test_get_create_club(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home_templates/create_club.html')

    def test_get_create_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_unsuccesful_create_club(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['name'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home_templates/create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))

    def test_succesful_create_club(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        club = Club.objects.get(name=self.form_input['name'])
        response_url = reverse('club_home', kwargs={'club_id': club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        club = Club.objects.get(name='PolecatChess2')
        self.assertEqual(club.location, 'London')
        self.assertEqual(club.description, 'Welcome to Polecat chess club!')
        club_owner = Membership.objects.get(club=club,
                                            role=Membership.OWNER).user
        self.assertEqual(club_owner, self.user)
        self.assertEqual(str(club), club.name)
