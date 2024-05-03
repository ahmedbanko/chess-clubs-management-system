"""Tests of the delete club view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Membership, Application, Club
from clubs.tests.helpers import reverse_with_next


class DeleteClubTestCase(TestCase):
    """Unit tests of the delete club view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(name='PolecatChess')
        self.user = User.objects.get(username='johndoe')
        self.user_application = Application.objects.create(
            user=self.user,
            club=self.club,
            personal_statement="User one personal statement",
            status=Application.ACCEPTED)
        self.membership = Membership.objects.create(user=self.user,
                                                    club=self.club,
                                                    role=Membership.OWNER)
        self.url = reverse('delete_club', kwargs={'club_id': self.club.id})

    def test_delete_club_url(self):
        self.client.login(email=self.user.email, password="Password123")
        self.assertEqual(self.url,
                         '/club/' + str(self.club.id) + '/delete_club')

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_delete_club(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'home_templates/delete_club.html')

    def test_get_delete_club_when_not_owner(self):
        self.client.login(email=self.user.email, password="Password123")
        self.membership.role = Membership.OFFICER
        self.membership.save()
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')

    def test_delete_club_when_owner(self):
        self.client.login(email=self.user.email, password="Password123")
        before_count = Club.objects.count()
        response = self.client.post(self.url, follow=True)
        after_count = Club.objects.count()
        redirect_url = reverse('dashboard')
        self.assertEqual(after_count, before_count - 1)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_delete_club_when_not_owner(self):
        self.client.login(email=self.user.email, password="Password123")
        self.membership.role = Membership.MEMBER
        self.membership.save()
        before_count = Club.objects.count()
        response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(response, 'home_templates/club_home.html')
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)

    def test_delete_club_you_are_not_a_member_of(self):
        self.client.login(email=self.user.email, password="Password123")
        before_count = Club.objects.count()
        url = reverse('delete_club', kwargs={'club_id': 2})
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, 'application_templates/application_list.html')
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)