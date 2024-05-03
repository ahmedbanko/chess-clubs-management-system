"""Tests of the club model."""

from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Club


class ClubTestCase(TestCase):
    """Unit tests of the club model."""
    def setUp(self):
        super(TestCase, self).setUp()
        self.club = Club(name="PoleCat Club",
                         location="London",
                         description="Welcome to PoleCat chess club!")

    def test_valid_club(self):
        try:
            self._assert_club_is_valid()
        except ValidationError:
            self.fail("Test club should be valid")

    def test_name_must_not_be_blank(self):
        self.club.name = ''
        self._assert_club_is_invalid()

    def test_name_can_contain_30_characters(self):
        self.club.name = 'x' * 30
        self._assert_club_is_valid()

    def test_name_must_not_be_over_30_characters_long(self):
        self.club.name = 'x' * 31
        self._assert_club_is_invalid()

    def test_description_must_not_be_blank(self):
        self.club.description = ''
        self._assert_club_is_invalid()

    def test_description_can_contain_520_characters(self):
        self.club.description = 'x' * 520
        self._assert_club_is_valid()

    def test_description_must_not_be_over_520_characters_long(self):
        self.club.description = 'x' * 521
        self._assert_club_is_invalid()

    def test_location_cannot_be_blank(self):
        self.club.location = ''
        self._assert_club_is_invalid()

    def test_location_can_contain_180_characters(self):
        self.club.location = 'x' * 180
        self._assert_club_is_valid()

    def test_location_must_not_be_over_180_characters_long(self):
        self.club.location = 'x' * 181
        self._assert_club_is_invalid()

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()