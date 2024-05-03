"""The models that represent the users and their membership in a club."""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from libgravatar import Gravatar
from clubs.models.helpers import UserManager

class User(AbstractUser):
    """User model used for authentication and is used to keep track applications/memberships."""
    username = models.CharField(max_length=30, unique=True, validators=[
        RegexValidator(
            regex=r'^\w{3,}$',
            message='Username must consist of at least three alphanumericals'
        )
    ])
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    bio = models.CharField(max_length=520, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Replaces default user manager with a costum one.
    objects = UserManager()

    # Status options for  the chess experience level
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

    EXPERIENCE_LEVELS = [
        (BEGINNER, "Beginner"),
        (INTERMEDIATE, "Intermediate"),
        (ADVANCED, "Advanced"),
    ]

    experience_level = models.CharField(
        blank=False,
        max_length=12,
        choices=EXPERIENCE_LEVELS,
        default=BEGINNER,
    )

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar which is derived from the email."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to the user's mini gravatar which is derived from the email."""
        return self.gravatar(size=50)

    def full_name(self):
        """Returns the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def is_member(self):
        """Returns whether the user is a member in at least one club."""
        return len(Membership.objects.filter(user=self, role=Membership.MEMBER)) != 0

    def is_owner(self):
        """Returns whether the user is an owner in at least one club."""
        return len(Membership.objects.filter(user=self, role=Membership.OWNER)) != 0

    def is_officer(self):
        """Returns whether the user is an officer in at least one club."""
        return len(Membership.objects.filter(user=self, role=Membership.OFFICER)) != 0

    def is_member_of(self, club):
        """Returns whether the user is a member in a given club."""
        return len(Membership.objects.filter(user=self, role=Membership.MEMBER, club=club)) != 0

    def is_owner_of(self, club):
        """Returns whether a user is the owner of a given club."""
        return len(Membership.objects.filter(user=self, role=Membership.OWNER, club=club)) != 0

    def is_officer_of(self, club):
        """Returns whether a user is an officer of a given club."""
        return len(Membership.objects.filter(user=self, role=Membership.OFFICER, club=club)) != 0

    def clubs(self):
        """Returns a list of clubs that the user currently has a membership in."""
        membership = Membership.objects.filter(user=self)
        return Club.objects.filter(membership__in=membership)

    class Meta:
        """Model options, to provide ordering for the user model."""
        ordering = ['first_name', 'last_name']


class Club(models.Model):
    """Club model used for creating clubs."""
    name = models.CharField(max_length=30, unique=True, blank=False)
    location = models.CharField(max_length=180, unique=False, blank=False)
    description = models.CharField(max_length=520, blank=False)

    def __str__(self):
        """Returns the name of the club for the admin interface"""
        return self.name 

    def get_owner(self):
        """Returns the user of the club."""
        return Membership.objects.get(club=self,role=Membership.OWNER).user

    def get_member_count(self):
        """Returns how many members there are in the club."""
        return len(Membership.objects.filter(club=self))

class Membership(models.Model):
    """Membership model used for roles within a club."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    # Role options for the different types of memberships
    MEMBER = "Member"
    OFFICER = "Officer"
    OWNER = "Owner"

    ROLE = [
        (MEMBER, "Member"),
        (OFFICER, "Officer"),
        (OWNER, "Owner"),
    ]

    role = models.CharField(max_length=8, choices=ROLE, default=MEMBER, blank=False)

    class Meta:
        """Model options, states that a user is allowed at maximum 
        1 membership per club."""
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'club'],
                name='one_membership_per_club'
            )
        ]
