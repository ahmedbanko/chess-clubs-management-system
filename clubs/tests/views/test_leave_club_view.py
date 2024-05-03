"""Tests of the leave club view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Membership, Application, Club
from clubs.tests.helpers import reverse_with_next


class LeaveClubTestCase(TestCase):
    """Unit tests of the leave club view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(name='PolecatChess')
        self.user = User.objects.get(username='johndoe')
        self.user_application = Application.objects.create(
            user=self.user,
            club=self.club,
            personal_statement="User one personal statement")
        self.url = reverse('leave_club', kwargs={'club_id': self.club.id})

    def test_leave_club_url(self):
        self.client.login(email=self.user.email, password="Password123")
        self.user_application.status = Application.ACCEPTED
        self.user_application.save()
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        self.assertEqual(self.url, '/leave_club/' + str(self.club.id))

    def test_members_can_leave_club(self):
        self.client.login(email=self.user.email, password="Password123")
        self.user_application.status = Application.ACCEPTED
        self.user_application.save()
        self.assertEqual(
            1,
            len(
                Application.objects.filter(user=self.user,
                                           club=self.club,
                                           status=Application.ACCEPTED)))
        member = Membership.objects.create(user=self.user,
                                           club=self.club,
                                           role=Membership.MEMBER)
        member.save()
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertEqual(
            0,
            len(
                Application.objects.filter(user=self.user,
                                           club=self.club,
                                           status=Application.ACCEPTED)))
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_officers_can_leave_club(self):
        self.client.login(email=self.user.email, password="Password123")
        self.user_application.status = Application.ACCEPTED
        self.user_application.save()
        self.assertEqual(
            1,
            len(
                Application.objects.filter(user=self.user,
                                           club=self.club,
                                           status=Application.ACCEPTED)))
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertEqual(
            0,
            len(
                Application.objects.filter(user=self.user,
                                           club=self.club,
                                           status=Application.ACCEPTED)))
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_owner_can_not_leave_club(self):
        self.client.login(email=self.user.email, password="Password123")
        self.user_application.status = Application.ACCEPTED
        self.user_application.save()
        self.assertEqual(
            1,
            len(
                Application.objects.filter(user=self.user,
                                           club=self.club,
                                           status=Application.ACCEPTED)))
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OWNER)
        response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        redirect_url = reverse('leave_club', kwargs={'club_id': self.club.id})
        self.assertEqual(
            1,
            len(
                Application.objects.filter(user=self.user,
                                           club=self.club,
                                           status=Application.ACCEPTED)))
        self.assertEqual(redirect_url, self.url)

    def test_not_a_member_can_not_leave(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('applications')
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_leave_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_post_leave_club_redirects_with_non_existing_club(self):
        self.client.login(email=self.user.email, password="Password123")
        Membership.objects.create(user=self.user, club=self.club)
        redirect_url = reverse('dashboard')
        response = self.client.post(
            reverse('leave_club', kwargs={'club_id': self.club.id + 9999}))
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_leave_club(self):
        self.client.login(email=self.user.email, password="Password123")
        self.user_application.status = Application.ACCEPTED
        self.user_application.save()
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OWNER)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)