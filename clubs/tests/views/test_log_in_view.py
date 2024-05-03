""" Tests of the log in view."""

from django.test import TestCase
from django.urls import reverse
from clubs.forms import LogInForm
from clubs.models import User
from clubs.tests.helpers import LogInTester, MenuTesterMixin, reverse_with_next
from django.contrib import messages


class LogInViewTestCase(TestCase, LogInTester, MenuTesterMixin):
    """Unit tests of the log in view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.get(username='johndoe')

    def test_log_in_url(self):
        self.assertEqual(self.url, '/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'authentication_templates/log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(next)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.assert_no_menu(response)

    def test_get_log_in_with_redirect(self):
        destination_url = reverse('dashboard')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'authentication_templates/log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(next, destination_url)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_login_redirect_when_logged_in(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'account_templates/dashboard.html')

    def test_unsuccesful_log_in(self):
        form_input = {'email': self.user.email, 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'authentication_templates/log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_succesful_log_in(self):
        form_input = {'email': self.user.email, 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('dashboard')
        self.assertRedirects(response,
                             response_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'account_templates/dashboard.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.assert_logged_in_menu(response)

    def test_succesful_log_in_with_redirect(self):
        redirect_url = reverse('dashboard')
        form_input = {
            'email': self.user.email,
            'password': 'Password123',
            'next': redirect_url
        }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'account_templates/dashboard.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_post_log_in_with_incorrect_credentials_and_redirect(self):
        redirect_url = reverse('dashboard')
        form_input = {
            'email': self.user.email,
            'password': 'WrongPassword123',
            'next': redirect_url
        }
        response = self.client.post(self.url, form_input)
        next = response.context['next']
        self.assertEqual(next, redirect_url)

    def test_log_in_with_blank_email(self):
        form_input = {'email': '', 'password': 'Password123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'authentication_templates/log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = {'email': self.user.email, 'password': ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'authentication_templates/log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_post_login_redirect_when_logged_in(self):
        self.client.login(email=self.user.email, password="Password123")
        form_input = {'email': 'WrongUSer', 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response,
                             redirect_url,
                             status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'account_templates/dashboard.html')

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = {'email': self.user.email, 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'authentication_templates/log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
