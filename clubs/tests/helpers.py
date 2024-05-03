from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin

class LogInTester:
    """Helper class that lets us check if there is a user logged in."""
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

"""Reverse users to next url if exists"""
def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url

class MenuTesterMixin(AssertHTMLMixin):
    logged_in_menu_urls = [
        reverse('user_matches'),
        reverse('applications'),
        reverse('profile'),
        reverse('log_out')
    ]

    def assert_logged_in_menu(self, response):
        for url in self.logged_in_menu_urls:
            with self.assertHTML(response, f'a[href="{url}"]'):
                pass

    def assert_no_menu(self, response):
        for url in self.logged_in_menu_urls:
            self.assertNotHTML(response, f'a[href="{url}"]')

    def assert_member_menu(self, response, club_id):        
        member_menu_urls = self._get_member_urls(club_id)
        officer_menu_urls = self._get_officer_urls(club_id)

        for url in member_menu_urls:
            with self.assertHTML(response, f'a[href="{url}"]'):
                pass

        for url in officer_menu_urls:
            self.assertNotHTML(response, f'a[href="{url}"]')

    def assert_officer_menu(self, response, club_id):
        member_menu_urls = self._get_member_urls(club_id)
        officer_menu_urls = self._get_officer_urls(club_id)

        for url in member_menu_urls:
            with self.assertHTML(response, f'a[href="{url}"]'):
                pass

        for url in officer_menu_urls:
            with self.assertHTML(response, f'a[href="{url}"]'):
                pass

    def assert_no_club_menu(self, response, club_id):
        member_menu_urls = self._get_member_urls(club_id)
        officer_menu_urls = self._get_officer_urls(club_id)

        for url in member_menu_urls:
            self.assertNotHTML(response, f'a[href="{url}"]')

        for url in officer_menu_urls:
            self.assertNotHTML(response, f'a[href="{url}"]')

    def _get_member_urls(self, club_id):
        return [
            reverse('club_home', kwargs={'club_id': club_id}),
            reverse('members_list', kwargs={'club_id': club_id}),
        ]

    def _get_officer_urls(self, club_id):
        return [
            reverse('club_application_list', kwargs={'club_id': club_id})
        ]
