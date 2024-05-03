"""Tests of the members list view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.models import Application, Club
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next
from clubs.models import Membership


class UserListTest(TestCase, MenuTesterMixin):
    """Unit tests of the members list view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(name='PolecatChess')
        self.url = reverse('members_list', kwargs={'club_id': self.club.id})
        self.first_user = User.objects.get(username='johndoe')
        self.user1application = Application.objects.create(
            user=self.first_user,
            club=self.club,
            personal_statement="1st user's personal statement")
        self.second_user = User.objects.get(username='janedoe')
        self.user2application = Application.objects.create(
            user=self.second_user,
            club=self.club,
            personal_statement="2nd user's personal statement")

    def test_members_list_url(self):
        self.assertEqual(self.url, '/club/' + str(self.club.id) + "/members/")

    def test_get_members_list(self):
        self.client.login(email=self.first_user.email, password='Password123')
        Membership.objects.create(user=self.first_user, club=self.club)
        self._create_test_users_in_same_club(15 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/members_list.html')
        self.assert_member_menu(response, self.club.id)
        self.assertEqual(len(response.context['members']), 15)
        for user_id in range(15 - 1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            user = User.objects.get(username=f'user{user_id}')
            user_url = reverse('show_user',
                               kwargs={
                                   'club_id': self.club.id,
                                   'user_id': user.id
                               })
            self.assertContains(response, user_url)
        self._delete_members()

    def test_does_not_show_users_in_different_club(self):
        self.client.login(email=self.first_user.email, password='Password123')
        Membership.objects.create(user=self.first_user, club=self.club)
        self._create_test_users_not_in_same_club(15 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/members_list.html')
        self.assert_member_menu(response, self.club.id)
        self.assertNotEqual(len(response.context['members']), 15)
        for user_id in range(15 - 1):
            self.assertNotContains(response, f'user{user_id}')
            self.assertNotContains(response, f'First{user_id}')
            self.assertNotContains(response, f'Last{user_id}')
            user = User.objects.get(username=f'user{user_id}')
            user_url = reverse('show_user',
                               kwargs={
                                   'club_id': self.club.id,
                                   'user_id': user.id
                               })
            self.assertNotContains(response, user_url)

    def test_get_members_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_member_cannot_promote_member_to_an_officer(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        target_url = reverse('promote_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        response = self.client.get(target_url, follow=True)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.second_user.is_member())
        self.assertTrue(self.first_user.is_member())

    def test_officer_can_promote_member_to_an_officer(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        target_url = reverse('promote_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.second_user.is_officer())
        self.assertTrue(self.first_user.is_officer())

    def test_officer_cannot_promote_an_existing_officer_again(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        target_url = reverse('promote_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.second_user.is_officer())
        self.assertTrue(self.first_user.is_officer())

    def test_officer_cannot_convert_an_owner_to_officer(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.OWNER)
        target_url = reverse('promote_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.second_user.is_owner())
        self.assertTrue(self.first_user.is_officer())

    def test_owner_can_promote_member_to_an_officer(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OWNER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        target_url = reverse('promote_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.second_user.is_officer())
        self.assertTrue(self.first_user.is_owner())

    def test_promote_member_with_invalid_id(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        target_url = reverse('promote_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': 99999
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.first_user.is_officer())
        self.assertEqual(len(Membership.objects.filter(user=99999)), 0)

    def test_member_cannot_demote_officer_to_a_member(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        target_url = reverse('demote_officer',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.second_user.is_officer())
        self.assertTrue(self.first_user.is_member())

    def test_officer_cannot_demote_another_officer(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        target_url = reverse('demote_officer',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.second_user.is_officer())
        self.assertTrue(self.first_user.is_officer())

    def test_owner_can_demote_an_officer(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OWNER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        target_url = reverse('demote_officer',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.second_user.is_member())
        self.assertTrue(self.first_user.is_owner())

    def test_owner_cannot_demote_himself(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OWNER)
        target_url = reverse('demote_officer',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.first_user.id
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.first_user.is_owner())

    def test_demote_officer_with_invalid_id(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OWNER)
        target_url = reverse('demote_officer',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': 99999
                             })
        response = self.client.post(target_url, follow=True)
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTrue(self.first_user.is_owner())
        self.assertEqual(len(Membership.objects.filter(user=99999)), 0)

    def test_member_cannot_delete_other_member(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        target_url = reverse('delete_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        members_before = Membership.objects.count
        response = self.client.post(target_url, follow=True)
        members_after = Membership.objects.count
        redirect_url = reverse('club_home', kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(members_before, members_after)
        self.assertNotEqual(
            len(Membership.objects.filter(user=self.second_user)), 0)

    def test_officer_cannot_delete_other_officer(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        target_url = reverse('delete_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        members_before = Membership.objects.count
        response = self.client.post(target_url, follow=True)
        members_after = Membership.objects.count
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(members_before, members_after)
        self.assertNotEqual(
            len(Membership.objects.filter(user=self.second_user)), 0)

    def test_officer_can_delete_member(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        self.user1application.save()
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.user2application.status = Application.ACCEPTED
        self.user2application.save()
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        target_url = reverse('delete_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        members_before = Membership.objects.count()
        response = self.client.post(target_url, follow=True)
        members_after = Membership.objects.count()
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(members_after, members_before - 1)
        self.assertEqual(len(Membership.objects.filter(user=self.second_user)),
                         0)

    def test_officer_cannot_delete_owner(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.user2application.status = Application.ACCEPTED
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.OWNER)
        target_url = reverse('delete_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        members_before = Membership.objects.count()
        response = self.client.post(target_url, follow=True)
        members_after = Membership.objects.count()
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(members_after, members_before)
        self.assertEqual(len(Membership.objects.filter(user=self.second_user)),
                         1)

    def test_owner_can_delete_officer(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        self.user1application.save()
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OWNER)
        self.user2application.status = Application.ACCEPTED
        self.user2application.save()
        Membership.objects.create(user=self.second_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        target_url = reverse('delete_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': self.second_user.id
                             })
        members_before = Membership.objects.count()
        response = self.client.post(target_url, follow=True)
        members_after = Membership.objects.count()
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(members_after, members_before - 1)
        self.assertEqual(len(Membership.objects.filter(user=self.second_user)),
                         0)

    def test_delete_member_with_invalid_id(self):
        self.client.login(email=self.first_user.email, password='Password123')
        self.user1application.status = Application.ACCEPTED
        Membership.objects.create(user=self.first_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        target_url = reverse('delete_member',
                             kwargs={
                                 'club_id': self.club.id,
                                 'user_id': 999999
                             })
        members_before = Membership.objects.count()
        response = self.client.post(target_url, follow=True)
        members_after = Membership.objects.count()
        redirect_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(members_after, members_before)

    def _create_test_users_in_same_club(self, user_count=10):
        for user_id in range(user_count):
            new_user = User.objects.create_user(
                username=f'user{user_id}',
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
            )
            Membership.objects.create(user=new_user, club=self.club)

    def _delete_members(self):
        for member in Membership.objects.all():
            member.delete()

    def _create_test_users_not_in_same_club(self, user_count=10):
        for user_id in range(user_count):
            User.objects.create_user(
                username=f'user{user_id}',
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
            )
