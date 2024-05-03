"""Tests of the application model."""

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from clubs.models import Application
from clubs.models import User, Club


class ApplicationTestCase(TestCase):
    """Unit tests of the application model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='PolecatChess')
        self.different_club = Club.objects.get(name='PolecatChess_2')
        self.application = self._create_application(self.user, self.club)

    def test_valid_application(self):
        try:
            self._assert_application_is_valid()
        except ValidationError:
            self.fail("Test application should be valid")

    def test_user_must_not_be_blank(self):
        self.application.user = None
        self._assert_application_is_invalid()

    def test_delete_application_when_user_is_deleted(self):
        self.user.delete()
        self._assert_application_is_invalid()

    def test_club_must_not_be_blank(self):
        self.application.club = None
        self._assert_application_is_invalid()

    def test_delete_application_when_club_is_deleted(self):
        self.club.delete()
        self._assert_application_is_invalid()

    def test_personal_statement_must_not_be_blank(self):
        self.application.personal_statement = ''
        self._assert_application_is_invalid()

    def test_personal_statement_can_contain_500_characters(self):
        self.application.personal_statement = 'x' * 500
        self._assert_application_is_valid()

    def test_personal_statement_must_not_be_over_500_characters_long(self):
        self.application.personal_statement = 'x' * 501
        self._assert_application_is_invalid()

    def test_status_cannot_be_blank(self):
        self.application.status = ''
        self._assert_application_is_invalid()

    def test_status_cannot_be_anything_but_a_status_constant(self):
        self.application.status = 'x'
        self._assert_application_is_invalid()

    def test_getter_functions_return_rightn_values(self):
        self.assertEqual(True, self.application.is_pending())
        self.application.status = Application.ACCEPTED
        self.assertEqual(True, self.application.is_accepted())
        self.application.status = Application.REJECTED
        self.assertEqual(True, self.application.is_rejected())

    def test_user_can_have_more_pending_application_to_different_clubs(self):
        count_before = Application.objects.count()
        self.application = self._create_application(self.user,
                                                    self.different_club)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before + 1)

    def test_user_can_have_more_accepted_application_to_different_clubs(self):
        self.application.status = Application.ACCEPTED
        self.application.save()
        count_before = Application.objects.count()
        self.application = self._create_application(self.user,
                                                    self.different_club)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before + 1)

    def test_user_can_have_more_not_pending_applications_to_different_clubs(
            self):
        self.application.status = Application.REJECTED
        self.application.save()
        count_before = Application.objects.count()
        self.application = self._create_application(self.user,
                                                    self.different_club)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before + 1)

    def test_user_can_have_only_one_pending_application_to_the_same_club(self):
        count_before = Application.objects.count()
        with self.assertRaises(IntegrityError):
            self.application = self._create_application(self.user, self.club)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before)

    def test_user_can_have_only_one_accepted_application_to_the_same_club(
            self):
        self.application.status = Application.ACCEPTED
        self.application.save()
        count_before = Application.objects.count()
        with self.assertRaises(IntegrityError):
            self.application = self._create_application(self.user, self.club)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before)

    def test_user_can_have_more_not_pending_applications_to_the_same_club(
            self):
        self.application.status = Application.REJECTED
        self.application.save()
        count_before = Application.objects.count()
        self.application = self._create_application(self.user, self.club)
        count_after = Application.objects.count()
        self.assertEqual(count_after, count_before + 1)

    def _assert_application_is_valid(self):
        try:
            self.application.full_clean()
        except (ValidationError):
            self.fail('Test application should be valid')

    def _assert_application_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.application.full_clean()

    def _create_application(self, user, club):
        return Application.objects.create(
            user=user, club=club, personal_statement="personal statement")
