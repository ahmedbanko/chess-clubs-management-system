"""Tests of the user model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Membership


class UserModelTestCase(TestCase):
    """Unit tests of the User model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/other_clubs.json',
    ]

    def setUp(self):
        self.user1 = User.objects.get(username='johndoe')
        self.user2 = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='PolecatChess')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user1.username = ''
        self._assert_user_is_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user1.username = 'x' * 30
        self._assert_user_is_valid()

    def test_username_cannot_be_over_30_characters_long(self):
        self.user1.username = 'x' * 31
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        self.user1.username = self.user2.username
        self._assert_user_is_invalid()

    def test_username_must_contain_only_alphanumericals_after_at(self):
        self.user1.username = 'john!doe'
        self._assert_user_is_invalid()

    def test_username_must_contain_at_least_3_alphanumericals(self):
        self.user1.username = 'jo'
        self._assert_user_is_invalid()

    def test_username_may_contain_numbers(self):
        self.user1.username = 'j0hndoe2'
        self._assert_user_is_valid()

    def test_first_name_must_not_be_blank(self):
        self.user1.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        self.user1.first_name = self.user2.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user1.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user1.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user1.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        self.user1.last_name = self.user2.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user1.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user1.last_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user1.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):

        self.user1.email = self.user2.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user1.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user1.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user1.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user1.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user1.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_bio_may_be_blank(self):
        self.user1.bio = ''
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):

        self.user1.bio = self.user2.bio
        self._assert_user_is_valid()

    def test_bio_may_contain_520_characters(self):
        self.user1.bio = 'x' * 520
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_520_characters(self):
        self.user1.bio = 'x' * 521
        self._assert_user_is_invalid()

    def test_experience_level_must_not_be_blank(self):
        self.user1.experience_level = ''
        self._assert_user_is_invalid()

    def test_experience_level_need_not_be_unique(self):

        self.user1.experience_level = self.user2.experience_level
        self._assert_user_is_valid

    def test_experience_level_must_be_one_of_choices(self):
        self.user1.experience_level = 'x'
        self._assert_user_is_invalid()

    def test_gravatar_returns_a_url(self):
        self.assertTrue(self.user1.gravatar().startswith(
            "https://www.gravatar.com/avatar/"))

    def test_mini_gravatar_returns_a_url(self):
        self.assertTrue(self.user1.mini_gravatar().startswith(
            "https://www.gravatar.com/avatar/"))

    def test_full_name_is_first_name_and_last_name(self):
        self.assertEqual(self.user1.full_name(),
                         self.user1.first_name + " " + self.user1.last_name)

    def test_user_does_not_have_roles_by_default(self):
        self.assertFalse(self.user1.is_member())
        self.assertFalse(self.user1.is_officer())
        self.assertFalse(self.user1.is_owner())

    def test_user_is_member_when_added_to_membership(self):
        Membership.objects.create(user=self.user1,
                                  club=self.club,
                                  role=Membership.MEMBER)
        self.assertTrue(self.user1.is_member())
        self.assertFalse(self.user1.is_officer())
        self.assertFalse(self.user1.is_owner())
        Membership.objects.get(user=self.user1).delete()

    def test_user_is_member_of_only_added_club_when_added_to_membership(self):
        club = Club.objects.get(name='PolecatChess_2')
        Membership.objects.create(user=self.user1,
                                  club=self.club,
                                  role=Membership.MEMBER)
        self.assertFalse(self.user1.is_member_of(club))
        self.assertFalse(self.user1.is_officer_of(club))
        self.assertFalse(self.user1.is_owner_of(club))
        Membership.objects.get(user=self.user1).delete()

    def test_user_is_officer_when_added_to_membership(self):
        Membership.objects.create(user=self.user1,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.assertFalse(self.user1.is_member())
        self.assertTrue(self.user1.is_officer())
        self.assertFalse(self.user1.is_owner())
        Membership.objects.get(user=self.user1).delete()

    def test_user_is_officer_of_only_added_club_when_added_to_membership(self):
        club = Club.objects.get(name='PolecatChess_2')
        Membership.objects.create(user=self.user1,
                                  club=self.club,
                                  role=Membership.OFFICER)
        self.assertFalse(self.user1.is_member_of(club))
        self.assertFalse(self.user1.is_officer_of(club))
        self.assertFalse(self.user1.is_owner_of(club))
        Membership.objects.get(user=self.user1).delete()

    def test_user_is_owner_when_added_to_membership(self):
        Membership.objects.create(user=self.user1,
                                  club=self.club,
                                  role=Membership.OWNER)
        self.assertFalse(self.user1.is_member())
        self.assertFalse(self.user1.is_officer())
        self.assertTrue(self.user1.is_owner())
        Membership.objects.get(user=self.user1).delete()

    def test_user_is_owner_of_only_added_club_when_added_to_membership(self):
        club = Club.objects.get(name='PolecatChess_2')
        Membership.objects.create(user=self.user1,
                                  club=self.club,
                                  role=Membership.OWNER)
        self.assertFalse(self.user1.is_member_of(club))
        self.assertFalse(self.user1.is_officer_of(club))
        self.assertFalse(self.user1.is_owner_of(club))
        Membership.objects.get(user=self.user1).delete()

    def test_create_super_user(self):
        super_user = User.objects.create_superuser(email="admin@example.com",
                                                   password="Password123")
        self.assertEquals(super_user.username, "admin")

    def test_create_super_user_raises_error_when_no_password_is_supplied(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="admin@example.com",
                                          password=None)

    def _assert_user_is_valid(self):
        try:
            self.user1.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user1.full_clean()