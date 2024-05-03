"""Tests of the reject application view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Application, Club
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next
from clubs.models import Membership


class ClubApplicationsViewTestCase(TestCase, MenuTesterMixin):
    """Unit tests of the reject application view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username="janedoe")
        self.club = Club.objects.get(name='PolecatChess')
        self.applicant = User.objects.get(username='johndoe')
        self.application = Application.objects.create(
            user=self.applicant,
            club=self.club,
            personal_statement="My personal statement")
        self.url = reverse('reject_application',
                           kwargs={
                               'club_id': self.club.id,
                               'application_id': self.application.id
                           })

    def test_reject_application_url(self):
        self.assertEqual(
            self.url, '/club/' + str(self.club.id) + '/reject_application/' +
            str(self.application.id))

    def test_reject_application(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.OFFICER)
        redirect_url = reverse('club_application_list',
                               kwargs={'club_id': self.club.id})
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEquals(
            Application.objects.get(id=self.application.id).status,
            Application.REJECTED)
        self.assertEquals(
            len(Membership.objects.filter(user=self.application.user)), 0)
        member.delete()

    def test_reject_rejected_application(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.OFFICER)
        self.application.status = Application.REJECTED
        self.application.save()
        redirect_url = reverse('club_application_list',
                               kwargs={'club_id': self.club.id})
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEquals(
            Application.objects.get(id=self.application.id).status,
            Application.REJECTED)
        self.assertEquals(
            len(Membership.objects.filter(user=self.application.user)), 0)
        member.delete()

    def test_reject_accepted_application_does_not_reject(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.OFFICER)
        self.application.status = Application.ACCEPTED
        self.application.save()
        redirect_url = reverse('club_application_list',
                               kwargs={'club_id': self.club.id})
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEquals(
            Application.objects.get(id=self.application.id).status,
            Application.ACCEPTED)
        self.assertEquals(
            len(Membership.objects.filter(user=self.application.user)), 0)
        member.delete()

    def test_reject_application_redirects_without_membership(self):
        self.client.login(email=self.user.email, password='Password123')
        redirect_url = reverse('applications')
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEquals(
            Application.objects.get(id=self.application.id).status,
            Application.PENDING)
        self.assertEquals(
            len(
                Membership.objects.filter(user=self.application.user,
                                          club=self.application.club)), 0)

    def test_reject_application_redirects_without_officer_permissions(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.MEMBER)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEquals(
            Application.objects.get(id=self.application.id).status,
            Application.PENDING)
        self.assertEquals(
            len(
                Membership.objects.filter(
                    user=self.application.user,
                    club=self.application.club,
                )), 0)
        member.delete()

    def test_reject_application_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEquals(
            Application.objects.get(id=self.application.id).status,
            Application.PENDING)
        self.assertEquals(
            len(
                Membership.objects.filter(
                    user=self.application.user,
                    club=self.application.club,
                )), 0)

    def test_reject_application_with_invalid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.OFFICER)
        url = reverse('reject_application',
                      kwargs={
                          'club_id': self.club.id,
                          'application_id': self.application.id + 9999
                      })
        response = self.client.post(url, follow=True)
        response_url = reverse('club_application_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'club_templates/club_application_list.html')
        self.assert_officer_menu(response, self.club.id)
        member.delete()