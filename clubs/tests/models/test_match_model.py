"""Tests of the match model."""

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from clubs.models import User, Club, Match, Membership
from clubs.models import Application
from django.test import TestCase
import datetime
import pytz


class MatchTestCase(TestCase):
    """Unit tests of the match model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.utc = pytz.UTC
        self.user1 = User.objects.get(username='johndoe')
        self.user2 = User.objects.get(username='petrapickles')
        self.club = Club.objects.get(name='PolecatChess')
        self.match_time = self.utc.localize(
            datetime.datetime(2022, 9, 25, 14, 40))
        self.usr1application = self._create_application(self.user1)
        self.usr2application = self._create_application(self.user2)
        self.membership1 = self._create_membership(self.user1)
        self.membership2 = self._create_membership(self.user2)

        self.match = Match.objects.create(
            player_1=self.user1,
            player_2=self.user2,
            club=self.club,
            location="Bush House floor 6",
            date_time=self.match_time,
            status=Match.PENDING,
        )

    def test_valid_match(self):
        try:
            self._assert_match_is_valid()
        except ValidationError:
            self.fail("Test match should be valid")

    def test_player1_cannot_be_blank(self):
        self.match.player_1 = None
        self._assert_match_is_invalid()

    def test_player2_cannot_be_blank(self):
        self.match.player_2 = None
        self._assert_match_is_invalid()

    def test_delete_match_when_a_player1_is_deleted(self):
        self.user1.delete()
        self._assert_match_is_invalid()

    def test_delete_match_when_a_player2_is_deleted(self):
        self.user2.delete()
        self._assert_match_is_invalid()

    def test_delete_match_when_a_club_is_deleted(self):
        self.club.delete()
        self._assert_match_is_invalid()

    def test_club_must_not_be_blank(self):
        self.match.club = None
        self._assert_match_is_invalid()

    def test_location_must_not_be_blank(self):
        self.match.location = ''
        self._assert_match_is_invalid()

    def test_date_time_must_not_be_blank(self):
        self.match.date_time = ''
        self._assert_match_is_invalid()

    def test_status_must_not_be_blank(self):
        self.match.status = ''
        self._assert_match_is_invalid()

    def test_location_can_contain_100_characters(self):
        self.match.location = 'x' * 100
        self._assert_match_is_valid()

    def test_location_must_not_be_over_100_characters_long(self):
        self.match.location = 'x' * 101
        self._assert_match_is_invalid()

    def test_status_cannot_be_anything_but_a_status_constant(self):
        self.match.status = 'x'
        self._assert_match_is_invalid()

    def test_getter_functions_return_right_values(self):
        self.assertEqual(True, self.match.is_pending())
        self.match.status = Match.PLAYER1
        self.assertEqual(True, self.match.is_player_1_win())
        self.match.status = Match.PLAYER2
        self.assertEqual(True, self.match.is_player_2_win())
        self.match.status = Match.DRAW
        self.assertEqual(True, self.match.is_draw())
        self.match.status = Match.CANCELLED
        self.assertEqual(True, self.match.is_cancelled())

    def test_player1_can_have_multiple_pending_match_in_different_players(
            self):
        user3 = User.objects.get(username='janedoe')
        self._create_application(user3)
        self._create_membership(user3)
        count_before = Match.objects.count()
        Match.objects.create(
            player_1=self.user1,
            player_2=user3,
            club=self.club,
            location="Bush House floor 6",
            date_time=self.utc.localize(datetime.datetime(2022, 9, 26, 14,
                                                          40)),
            status=Match.PENDING,
        )
        count_after = Match.objects.count()
        self.assertEqual(count_after, count_before + 1)

    def test_player1_cannot_have_a_match_with_himself(self):
        self.match.player_1 = self.user1
        self.match.player_2 = self.user1
        with self.assertRaises(IntegrityError):
            self.match.save()

    def test_no_two_matches_with_identical_details(self):
        count_before = Match.objects.count()
        with self.assertRaises(IntegrityError):
            Match.objects.create(
                player_1=self.user1,
                player_2=self.user2,
                club=self.club,
                location="Bush House floor 6",
                date_time=self.match_time,
                status=Match.PENDING,
            ).save()
        count_after = Match.objects.count()
        self.assertEqual(count_after, count_before)

    def _assert_match_is_valid(self):
        try:
            self.match.full_clean()
        except (ValidationError):
            self.fail('Test application should be valid')
        Match.objects.all().delete()

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.match.full_clean()
        Match.objects.all().delete()

    def _create_application(self, user):
        return Application.objects.create(
            user=user,
            club=self.club,
            personal_statement="personal statement",
            status=Application.ACCEPTED)

    def _create_membership(self, user):
        return Membership.objects.create(user=user,
                                         club=self.club,
                                         role=Membership.MEMBER)
