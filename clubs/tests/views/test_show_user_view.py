"""Tests of the show user view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Membership, Application, Club, Match
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next
import datetime
import pytz


class ShowUserTest(TestCase, MenuTesterMixin):
    """Unit tests of the show user view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/other_clubs.json'
    ]

    def setUp(self):
        self.utc = pytz.UTC
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='PolecatChess')
        self.target_user = User.objects.get(username='janedoe')
        self.url = reverse('show_user',
                           kwargs={
                               'club_id': self.club.id,
                               'user_id': self.target_user.id
                           })
        self.application = Application.objects.create(
            user=self.user,
            club=self.club,
            personal_statement="Personal statement",
            status=Application.ACCEPTED)

        self.avaliable_options_in_dropbox = [
            self._reverse_with_club_id_and_target('transfer_ownership'),
            self._reverse_with_club_id_and_target('promote_member'),
            self._reverse_with_club_id_and_target('demote_officer'),
            self._reverse_with_club_id_and_target('delete_member'),
        ]

    def test_show_user_url(self):
        self.assertEqual(self.url,
                         f'/club/{self.club.id}/user/{self.target_user.id}')

    def test_get_show_user_with_valid_id_for_member(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user, club=self.club)
        Membership.objects.create(user=self.target_user, club=self.club)
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   personal_statement="Personal statement",
                                   status=Application.ACCEPTED)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/show_user.html')
        self.assert_member_menu(response, self.club.id)
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "janedoe")
        self.assertContains(response,
                            "The quick brown fox jumps over the lazy dog.")

    def test_get_show_user_not_allowed_for_not_member(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('members_list', kwargs={'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('applications')
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')
        self.assert_no_club_menu(response, self.club.id)

    def test_get_show_user_with_own_id_for_member(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.MEMBER)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.user.id
                      })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/show_user.html')
        self.assertContains(response, "John Doe")
        self.assertContains(response, "johndoe")
        self.assertContains(response, "Hello, I&#x27;m John Doe.")
        self._assert_conatins_forms_with_urls(response, [])

    def test_get_show_user_with_invalid_id_for_member(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user, club=self.club)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.user.id + 9999
                      })
        response = self.client.get(url, follow=True)
        response_url = reverse('members_list',
                               kwargs={'club_id': self.club.id})
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'club_templates/members_list.html')
        self.assert_member_menu(response, self.club.id)

    def test_get_show_user_with_valid_id_for_officer(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        Membership.objects.create(user=self.target_user, club=self.club)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.target_user.id
                      })
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   personal_statement="Personal statement",
                                   status=Application.ACCEPTED)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/show_user.html')
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "janedoe")
        self.assertContains(response,
                            "The quick brown fox jumps over the lazy dog.")
        self.assertContains(response, "janedoe@example.org")
        self.assertContains(response, "Beginner")
        self.assertContains(response, "Personal statement")
        self.assert_officer_menu(response, self.club.id)

    def test_get_show_user_with_valid_id_for_owner(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OWNER)
        Membership.objects.create(user=self.target_user, club=self.club)
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   personal_statement="Personal statement",
                                   status=Application.ACCEPTED)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.target_user.id
                      })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/show_user.html')
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "janedoe")
        self.assertContains(response,
                            "The quick brown fox jumps over the lazy dog.")
        self.assertContains(response, "janedoe@example.org")
        self.assertContains(response, "Beginner")
        self.assertContains(response, "Personal statement")
        self.assert_officer_menu(response, self.club.id)

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_memebr_stats_are_calculated_correctly(self):
        self._set_up_matches()
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.user.id
                      })
        response = self.client.get(url)
        self.assertEquals(response.context['wins'], 1)
        self.assertEquals(response.context['draws'], 0)
        self.assertEquals(response.context['losses'], 0)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.target_user.id
                      })
        response = self.client.get(url)
        self.assertEquals(response.context['wins'], 0)
        self.assertEquals(response.context['draws'], 0)
        self.assertEquals(response.context['losses'], 1)

    def test_memebr_clubs_are_correct_length_correctly(self):
        self._set_up_matches()
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.user.id
                      })
        response = self.client.get(url)
        self.assertEquals(len(response.context['upcoming_matches']), 0)
        self.assertEquals(len(response.context['previous_matches']), 1)

    def _set_up_matches(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user, club=self.club)
        Membership.objects.create(user=self.target_user, club=self.club)
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   status=Application.ACCEPTED)
        Match.objects.create(player_1=self.user,
                             player_2=self.target_user,
                             location='Bush House',
                             date_time=self.utc.localize(
                                 datetime.datetime(2022, 9, 25, 10, 30)),
                             club=self.club,
                             status=Match.PLAYER1)

        other_club = Club.objects.get(name='PolecatChess_2')
        Membership.objects.create(user=self.user, club=other_club)
        Application.objects.create(user=self.target_user,
                                   club=other_club,
                                   status=Application.ACCEPTED)
        Membership.objects.create(user=self.target_user, club=other_club)
        Application.objects.create(user=self.target_user,
                                   club=other_club,
                                   status=Application.ACCEPTED)
        Match.objects.create(player_1=self.user,
                             player_2=self.target_user,
                             location='Bush House',
                             date_time=self.utc.localize(
                                 datetime.datetime(2022, 10, 25, 10, 30)),
                             club=other_club,
                             status=Match.PLAYER1)

    def test_member_does_not_see_profile_dropbox(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user, club=self.club)
        other_member = Membership.objects.create(user=self.target_user,
                                                 club=self.club)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.target_user.id
                      })
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   personal_statement="Personal statement",
                                   status=Application.ACCEPTED)
        response = self.client.get(url)
        self._assert_conatins_forms_with_urls(response, [])
        other_member.role = Membership.OFFICER
        response = self.client.get(url)
        self._assert_conatins_forms_with_urls(response, [])
        other_member.role = Membership.OWNER
        response = self.client.get(url)
        self._assert_conatins_forms_with_urls(response, [])

    def test_officer_sees_promote_and_delete_for_member(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        Membership.objects.create(user=self.target_user, club=self.club)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.target_user.id
                      })
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   personal_statement="Personal statement",
                                   status=Application.ACCEPTED)
        response = self.client.get(url)
        self._assert_conatins_forms_with_urls(response, [
            self._reverse_with_club_id_and_target('promote_member'),
            self._reverse_with_club_id_and_target('delete_member'),
        ])

    def test_does_not_see_profile_dropbox_for_officer_and_owner(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        other_member = Membership.objects.create(user=self.target_user,
                                                 club=self.club,
                                                 role=Membership.OFFICER)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.target_user.id
                      })
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   personal_statement="Personal statement",
                                   status=Application.ACCEPTED)
        response = self.client.get(url)
        self._assert_conatins_forms_with_urls(response, [])
        other_member.role = Membership.OWNER
        response = self.client.get(url)
        self._assert_conatins_forms_with_urls(response, [])

    def test_owner_sees_promote_and_delete_for_member(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OWNER)
        Membership.objects.create(user=self.target_user, club=self.club)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.target_user.id
                      })
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   personal_statement="Personal statement",
                                   status=Application.ACCEPTED)
        response = self.client.get(url)
        self._assert_conatins_forms_with_urls(response, [
            self._reverse_with_club_id_and_target('promote_member'),
            self._reverse_with_club_id_and_target('delete_member'),
            self._reverse_with_club_id_and_target('transfer_ownership'),
        ])

    def test_owner_sees_demote_and_transfer_for_officer(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(user=self.user,
                                  club=self.club,
                                  role=Membership.OWNER)
        Membership.objects.create(user=self.target_user,
                                  club=self.club,
                                  role=Membership.OFFICER)
        url = reverse('show_user',
                      kwargs={
                          'club_id': self.club.id,
                          'user_id': self.target_user.id
                      })
        Application.objects.create(user=self.target_user,
                                   club=self.club,
                                   personal_statement="Personal statement",
                                   status=Application.ACCEPTED)
        response = self.client.get(url)
        self._assert_conatins_forms_with_urls(response, [
            self._reverse_with_club_id_and_target('demote_officer'),
            self._reverse_with_club_id_and_target('delete_member'),
            self._reverse_with_club_id_and_target('transfer_ownership'),
        ])

    def _reverse_with_club_id_and_target(self, base_url):
        return reverse(base_url,
                       kwargs={
                           'club_id': self.club.id,
                           'user_id': self.target_user.id
                       })

    def _assert_conatins_forms_with_urls(self, response, urls):
        for url in self.avaliable_options_in_dropbox:
            if url in urls:
                with self.assertHTML(response, f'form[action="{url}"]'):
                    pass
            else:
                self.assertNotHTML(response, f'form[action="{url}"]')
                pass

        if len(urls) == 0:
            self.assertNotHTML(response, f'.fas.fa-ellipsis-v')
