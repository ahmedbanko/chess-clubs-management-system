"""Tests of the new application view."""

from django.test import TestCase
from django.urls import reverse
from clubs.forms import ApplicationForm
from clubs.models import User
from clubs.models import Application, Club
from clubs.tests.helpers import MenuTesterMixin, reverse_with_next


class ApplicationViewTestCase(TestCase, MenuTesterMixin):
    """Unit tests of the new application view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(name='PolecatChess')
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'club': 'PolecatChess',
            'personal_statement': 'My personal statement'
        }
        self.url = reverse('application')

    def test_application_url(self):
        self.assertEqual(self.url, '/application/')

    def test_get_application_form_when_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)

    def test_post_application_form_when_not_logged_in(self):
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse_with_next('log_in', self.url)
        before_count = Application.objects.count()
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_get_application(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/new_application.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplicationForm))
        self.assertFalse(form.is_bound)

    def test_get_application_with_preset_value(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        url = reverse('application', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/new_application.html')
        self.assert_no_club_menu(response, self.club.id)
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplicationForm))
        self.assertFalse(form.is_bound)

    def test_invalid_application(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        self.form_input['personal_statement'] = ''
        before_count = Application.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'application_templates/new_application.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplicationForm))
        self.assertTrue(form.is_bound)

    def test_valid_application(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        before_count = Application.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')
        application = Application.objects.get(user=self.user)
        self.assertEqual(application.personal_statement,
                         'My personal statement')

    def test_create_second_pending_application_for_same_club_not_allowed(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        before_count = Application.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Application.objects.count()
        self.assertEqual(
            str(list(response.context['messages'])[0]),
            'Application for this club has already been submitted')
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response,
                                'application_templates/new_application.html')

    def test_create_second_application_after_first_one_is_rejected_allowed(
            self):
        self.client.login(email='johndoe@example.org', password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        before_count = Application.objects.count()
        application = Application.objects.get(user=self.user)
        application.status = Application.REJECTED
        application.save()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertTemplateUsed(response,
                                'application_templates/application_list.html')

    def test_two_applciation_by_different_user_are_allowed(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        before_count = Application.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTemplateUsed(response, 'application_templates/application_list.html')
        User.objects.get(username='janedoe')
        self.client.login(email='janedoe@example.org', password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTemplateUsed(response, 'application_templates/application_list.html')
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 2)
