"""Tests of the membership model."""

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from clubs.models import Membership, User, Club


class MembershipModelTestCase(TestCase):
    """Unit tests of the membership model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='PolecatChess')
        self.membership = Membership.objects.create(user=self.user,
                                                    club=self.club,
                                                    role=Membership.MEMBER)

    def test_valid_membership(self):
        try:
            self._assert_membership_is_valid()
        except ValidationError:
            self.fail("Test membership should be valid")

    def test_user_must_not_be_blank(self):
        self.membership.user = None
        self._assert_membership_is_invalid()

    def test_delete_membership_when_user_is_deleted(self):
        self.user.delete()
        self._assert_membership_is_invalid()

    def test_role_cannot_be_blank(self):
        self.membership.role = ''
        self._assert_membership_is_invalid()

    def test_role_cannot_be_anything_but_a_role_constant(self):
        self.membership.role = 'x'
        self._assert_membership_is_invalid()

    def test_user_can_have_only_one_membership_to_the_same_club(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(user=self.user,
                                      club=self.club,
                                      role=Membership.MEMBER)

    def test_user_can_have_more_memberships_to_different_clubs(self):
        other_club = Club.objects.get(name='PolecatChess_2')
        second_membership = Membership.objects.create(user=self.user,
                                                      club=other_club,
                                                      role=Membership.MEMBER)
        try:
            second_membership.full_clean()
        except (ValidationError):
            self.fail('Test membership should be valid')

    def _assert_membership_is_valid(self):
        try:
            self.membership.full_clean()
        except (ValidationError):
            self.fail('Test membership should be valid')

    def _assert_membership_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.membership.full_clean()
