"""Tests of the club applications view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Application, Membership
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next


class ClubApplicationsViewTestCase(TestCase, MenuTesterMixin):
    """Unit tests of the club applications view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='PolecatChess')
        self.url = reverse('club_application_list',
                           kwargs={'club_id': self.club.id})

    def test_club_application_list_url(self):
        self.assertEqual(self.url,
                         '/club/' + str(self.club.id) + "/applications/")

    def test_club_application_list(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.OFFICER)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/club_application_list.html')
        self.assert_officer_menu(response, self.club.id)
        applications = response.context['applications']
        self.assertEquals(
            len(applications),
            len(
                Application.objects.filter(status=Application.PENDING,
                                           club=self.club)))
        member.delete()

    def test_get_club_application_list_redirects_without_membership(self):
        self.client.login(email=self.user.email, password='Password123')
        redirect_url = reverse('applications')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_club_application_list_redirects_without_officer_permissions(
            self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.MEMBER)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        member.delete()

    def test_get_club_application_list_redirects_with_invalid_club_id(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.OFFICER)
        redirect_url = reverse('dashboard')
        invalid_url = reverse('club_application_list',
                              kwargs={'club_id': self.club.id + 999})
        response = self.client.get(invalid_url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        member.delete()

    def test_get_club_application_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
