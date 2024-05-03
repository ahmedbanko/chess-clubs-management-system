"""Seeder which creates users, clubs as well as memeberships and matches for the clubs."""

from datetime import datetime
from django.core.management.base import BaseCommand
from faker import Faker
import pytz
from clubs.models import User, Application, Membership, Club, Match
import random

class Command(BaseCommand):
    """The database seeder."""
    PASSWORD = "Password123"
    APPLICANT_COUNT = 10
    MEMBER_COUNT = 15
    OFFICER_COUNT = 1
    PAST_MATCH_COUNT = 10
    PENDING_MATCH_COUNT = 10
    FUTURE_MATCH_COUNT = 10

    def __init__(self):
        """Intialises faker and timezone manager."""
        super().__init__()
        self.utc = pytz.UTC
        self.faker = Faker('en_GB')
        Faker.seed(2000)

    def handle(self, *args, **options):
        """Creates clubs, users as well as memeberships and matches for the clubs."""
        print("Seeding...")
        self._create_data_for_spec()
        self._create_random_data()
        print(f"User seeding complete.")
        print(f"Created {self.APPLICANT_COUNT} applicants in each club")
        print(f"Created {self.MEMBER_COUNT} members in each clubs")
        print(f"Created {self.OFFICER_COUNT} officers in each clubs")
        print("Also created preprogrammed members (jeb@example.org)," +
         " (val@example.org) and (billie@example.org).")

    def _create_data_for_spec(self):
        """Creates preprogrammed users and memberships."""
        kerbal_club = self._create_club("Kerbal Chess Club", "Central London")
        strand_club = self._create_club("Strand Chess Club", "Strand")
        waterloo_club = self._create_club("Waterloo Chess Club", "Waterloo")
        guys_club = self._create_club("Guy's Chess Club", "London Bridge")

        jane = self._create_user("Jane", "Doe")
        jeb = self._create_user("Jebediah", "Kerman", "jeb@example.org")
        val = self._create_user("Valentina", "Kerman", "val@example.org")
        billie = self._create_user("Billie", "Kerman", "billie@example.org")

        self._create_member(jane, kerbal_club, Membership.OWNER)
        self._create_member(jeb, kerbal_club)
        self._create_member(val, kerbal_club)
        self._create_member(billie, kerbal_club)

        self._create_member(jane, strand_club, Membership.OWNER)
        self._create_member(jeb, strand_club, Membership.OFFICER)
        self._create_member(val, strand_club)
        self._create_member(billie, strand_club)

        self._create_member(jane, waterloo_club, Membership.OFFICER)
        self._create_member(jeb, waterloo_club)
        self._create_member(val, waterloo_club, Membership.OWNER)
        self._create_member(billie, waterloo_club)

        self._create_member(jane, guys_club, Membership.OWNER)
        self._create_member(jeb, guys_club)
        self._create_member(val, guys_club)
        self._create_member(billie, guys_club)

    def _create_random_data(self):
        """Create some random users and memberships and applications."""
        clubs = Club.objects.all()
        
        for club in clubs:
            self.add_random_club_data(club)

    def add_random_club_data(self, club):
        """Sets up memberships and matches for the clubs."""
        for i in range(0, self.APPLICANT_COUNT):
            user = self._create_user(self.faker.first_name(), self.faker.last_name())
            Application.objects.create(
                user=user,
                club=club,
                personal_statement=f"{user.first_name} {user.last_name}'s personal statement"
            )
        
        for i in range(0, self.MEMBER_COUNT):
            user = self._create_user(self.faker.first_name(), self.faker.last_name())
            self._create_member(user, club)

        for i in range(0, self.OFFICER_COUNT):
            user = self._create_user(self.faker.first_name(), self.faker.last_name())
            self._create_member(user, club, Membership.OFFICER)

        self._generate_past_matches(club)
        self._generate_pending_matches(club)
        self._generate_future_matches(club)
        
    def _generate_past_matches(self, club):
        """Generate matches with past results which cannot be edited."""
        for other_user in range(0, self.PAST_MATCH_COUNT):
            user = self.random_memberships(club).first().user
            other_user = self.random_memberships(club).exclude(user=user).first().user

            while self._has_already_played_match(user, other_user):
                user = self.random_memberships(club).first().user
                other_user = self.random_memberships(club).exclude(user=user).first().user

            random_number = random.randint(1, 10)
            status = Match.PLAYER1
            
            if random_number >= 4:
                status = Match.PLAYER2
            
            if random_number >= 9: 
                status = Match.DRAW

            self.match = Match.objects.create(
                player_1=user,
                player_2=other_user,
                club=club,
                location=club.location,
                date_time=self.utc.localize(self.faker.date_time_between()),
                status=status,
            )

    def _generate_pending_matches(self, club):
        """Generate matches without past results so they are editable."""
        for other_user in range(0, self.PENDING_MATCH_COUNT):
            user = self.random_memberships(club).first().user
            other_user = self.random_memberships(club).exclude(user=user).first().user

            while self._has_already_played_match(user, other_user):
                user = self.random_memberships(club).first().user
                other_user = self.random_memberships(club).exclude(user=user).first().user

            self.match = Match.objects.create(
                player_1=user,
                player_2=other_user,
                club=club,
                location=club.location,
                date_time=self.utc.localize(self.faker.date_time_between()),
                status=Match.PENDING,
            )

    def _generate_future_matches(self, club):
        """Generate future matches results so they are cancellable."""
        for other_user in range(0, self.FUTURE_MATCH_COUNT):
            user = self.random_memberships(club).first().user
            other_user = self.random_memberships(club).exclude(user=user).first().user

            while self._has_already_played_match(user, other_user):
                user = self.random_memberships(club).first().user
                other_user = self.random_memberships(club).exclude(user=user).first().user

            self.match = Match.objects.create(
                player_1=user,
                player_2=other_user,
                club=club,
                location=club.location,
                date_time=self.utc.localize(self.faker.date_time_between_dates(
                    datetime_start=self.utc.localize(datetime.today()),
                    datetime_end=self.utc.localize(datetime(2030, 5, 17))
                )),
                status=Match.PENDING,
            )

    def _has_already_played_match(self, user, other_user):
        """Returns weather a match between two users exists already."""
        return self._exists_in_matches(user, other_user) or self._exists_in_matches(other_user, user)

    def _exists_in_matches(self, user, other_user):
        """Returns weather a user is part of a match."""
        return len(Match.objects.filter(player_1=other_user, player_2=user)) != 0

    def _create_club(self, name, location):
        """Create a club in the database."""
        return Club.objects.create(
            name=name,
            location=location,
            description=f"This the the {name}, come have fun!"
        )

    def _create_user(self, first_name, last_name, email="auto-generate"):
        """Create a user in the database with auto generated email unless specified."""
        if email == "auto-generate":
            email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        bio = f"{first_name} {last_name}'s Bio"
        return User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
            bio=bio
        )

    def _create_member(self, user, club, role=Membership.MEMBER):
        """Create a membership for the user in given club."""
        self._create_accepted_application(user, club)
        Membership.objects.create(user=user, role=role, club=club)

    def _create_accepted_application(self, user, club):
        """Create an accepted for the user in given club."""
        application = Application.objects.create(
            user=user,
            club=club,
            personal_statement=f"{user.first_name} {user.last_name}'s personal statement"
        )
        application.status = Application.ACCEPTED
        application.save()

    def _email(self, first_name, last_name):
        """Generates a email given the first and last name."""
        email = f'{first_name.lower()}.{last_name.lower()}@example.org'
        return email

    def _username(self, first_name, last_name):
        """Generates a username given the first and last name."""
        username = f'{first_name.lower()}{last_name.lower()}'
        return username

    def random_memberships(self, club):
        return Membership.objects.filter(club=club).order_by("?")