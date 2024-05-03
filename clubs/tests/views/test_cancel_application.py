"""Tests of the cancel application view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Application, Club
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next


class CancelApplicationViewTestCase(TestCase, MenuTesterMixin):
    """Unit tests of cancel application view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='PolecatChess')
        self.application = Application.objects.create(
            user=self.user,
            club=self.club,
            personal_statement="Application to cancel",
            status="Pending")
        self.url = reverse('cancel_application',
                           kwargs={'application_id': self.application.id})

    def test_cancel_application_url(self):
        self.assertEqual(
            self.url,
            f'/applications/cancel_application/{self.application.id}')

    def test_get_cancel_application_url(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')
        self.assert_no_club_menu(response, self.club.id)

    def test_post_cancel_application_url(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')

    def test_get_cancel_application_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_cancel_nonexisting_application(self):
        self.client.login(email=self.user.email, password='Password123')
        count_before = Application.objects.count()
        self.url = reverse('cancel_application',
                           kwargs={'application_id': 99999})
        response = self.client.get(self.url, follow=True)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')

    def test_cannot_cancel_application_not_belonging_to_the_logged_in_user(
            self):
        self.client.login(email=self.user.email, password='Password123')
        second_application = self._create_second_application_belonging_to_different_user(
        )
        count_before = Application.objects.count()
        self.url = reverse('cancel_application',
                           kwargs={'application_id': second_application.id})
        response = self.client.get(self.url, follow=True)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')

    def test_successful_cancel_application(self):
        self.client.login(email=self.user.email, password='Password123')
        count_before = Application.objects.count()
        response = self.client.get(self.url, follow=True)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before - 1)
        response_url = reverse('applications')
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')

    def test_cannot_cancel_accepted_application(self):
        self.client.login(email=self.user.email, password='Password123')
        count_before = len(Application.objects.all())
        self.application.status = Application.ACCEPTED
        self.application.save()
        response = self.client.get(self.url)
        count_after = len(Application.objects.all())
        self.assertEqual(count_after, count_before)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')

    def test_cannot_cancel_rejected_application(self):
        self.client.login(email=self.user.email, password='Password123')
        count_before = len(Application.objects.all())
        self.application.status = Application.REJECTED
        self.application.save()
        response = self.client.get(self.url)
        count_after = len(Application.objects.all())
        self.assertEqual(count_after, count_before)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')

    def _create_second_application_belonging_to_different_user(self):
        second_user = User.objects.get(username='janedoe')
        application = Application.objects.create(
            user=second_user,
            club=self.club,
            personal_statement="Application to cancel",
            status="Pending")
        return application