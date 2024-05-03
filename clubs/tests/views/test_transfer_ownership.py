"""Tests of the transfer ownership view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Application, Club
from clubs.models import Membership


class TransferOwnershipViewTestCase(TestCase):
    """Unit tests of the transfer ownership view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(name='PolecatChess')
        self.user_one = User.objects.get(username='johndoe')
        self.user_one_application = Application.objects.create(
            user=self.user_one,
            club=self.club,
            personal_statement="User one personal statement")
        self.user_two = User.objects.get(username='janedoe')
        self.user_two_application = Application.objects.create(
            user=self.user_two,
            club=self.club,
            personal_statement="User two personal statement")
        self.url = reverse('transfer_ownership',
                           kwargs={
                               'club_id': self.club.id,
                               'user_id': self.user_two.id
                           })

    def test_transfer_ownership_url(self):
        self.assertEqual(
            self.url,
            f'/club/{self.club.id}/transfer_ownership/{self.user_two.id}')

    def test_get_transfer_ownership_redirects_without_membership(self):
        self.client.login(email=self.user_one.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('applications')
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_transfer_ownership_redirects_as_member(self):
        self.client.login(email=self.user_one.email, password='Password123')
        self.user_one_application.status = Application.ACCEPTED
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.MEMBER)
        target_url = reverse('transfer_ownership',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.user_two.id
                             })
        response = self.client.get(target_url, follow=True)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_transfer_ownership_does_not_redirect_as_owner(self):
        self.client.login(email=self.user_one.email, password='Password123')
        self.user_one_application.status = Application.ACCEPTED
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.OWNER)
        response = self.client.get(self.url)
        self.assertTrue(response.status_code, 200)

    def test_post_transfer_ownership_as_owner(self):
        self.client.login(email=self.user_one.email, password='Password123')
        self.user_one_application.status = Application.ACCEPTED
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.OWNER)
        self.user_two_application.status = Application.ACCEPTED
        user_two_membership = Membership.objects.create(user=self.user_two,
                                                        club=self.club,
                                                        role=Membership.MEMBER)
        self.client.post(self.url, {'new_owner': user_two_membership.id})
        self.assertTrue(self.user_one.is_officer())
        self.assertTrue(self.user_two.is_owner())

    def test_get_transfer_ownership_as_owner(self):
        self.client.login(email=self.user_one.email, password='Password123')
        self.user_one_application.status = Application.ACCEPTED
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.OWNER)
        self.user_two_application.status = Application.ACCEPTED
        user_two_membership = Membership.objects.create(user=self.user_two,
                                                        club=self.club,
                                                        role=Membership.MEMBER)
        response = self.client.get(self.url,
                                   {'new_owner': user_two_membership.id})
        self.assertTrue(response.status_code, 200)

    def test_post_transfer_ownership_as_owner_to_self(self):
        self.client.login(email=self.user_one.email, password='Password123')
        self.user_one_application.status = Application.ACCEPTED
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.OWNER)
        target_url = reverse('transfer_ownership',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.user_one.id
                             })
        response = self.client.post(target_url)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(self.user_one.is_owner())

    def test_get_transfer_ownership_as_owner_to_self(self):
        self.client.login(email=self.user_one.email, password='Password123')
        self.user_one_application.status = Application.ACCEPTED
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.OWNER)
        target_url = reverse('transfer_ownership',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.user_one.id
                             })
        response = self.client.get(target_url)
        self.assertTrue(self.user_one.is_owner())
        self.club = Club.objects.get(name='PolecatChess')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_transfer_ownership_non_existing_user(self):
        self.client.login(email=self.user_one.email, password='Password123')
        self.user_one_application.status = Application.ACCEPTED
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.OWNER)
        target_url = reverse('transfer_ownership',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.user_one.id + 9999
                             })
        response = self.client.get(target_url)
        self.assertTrue(self.user_one.is_owner())
        self.club = Club.objects.get(name='PolecatChess')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_post_transfer_ownership_non_existing_user(self):
        self.client.login(email=self.user_one.email, password='Password123')
        self.user_one_application.status = Application.ACCEPTED
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.OWNER)
        target_url = reverse('transfer_ownership',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.user_one.id + 9999
                             })
        response = self.client.post(target_url)
        self.assertTrue(self.user_one.is_owner())
        self.club = Club.objects.get(name='PolecatChess')
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_get_transfer_ownership_redirects_with_invalid_club_id(self):
        self.client.login(email=self.user_one.email, password='Password123')
        Membership.objects.create(user=self.user_one,
                                  club=self.club,
                                  role=Membership.OWNER)
        redirect_url = reverse('dashboard')
        invalid_url = reverse('transfer_ownership',
                              kwargs={
                                  'club_id': self.club.id + 9999,
                                  'user_id': self.user_one.id
                              })
        response = self.client.get(invalid_url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
