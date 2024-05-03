"""The models that map to the application between a user and a club."""

from django.db import models
from clubs.models import User
from clubs.models import Club
from django.db.utils import IntegrityError

class Application(models.Model):
    """Application model used for creating an application to club for a given user."""
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        blank = False,
        null = False,
    )

    club = models.ForeignKey(
        Club,
        on_delete = models.CASCADE,
        blank = False,
        null = False,
    )

    personal_statement = models.CharField(unique = False, max_length = 500, blank = False)

    # Status options
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    
    STATUS = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    ]

    status = models.CharField(max_length = 8, choices = STATUS, default = PENDING, blank = False)

    created_at = models.DateTimeField(auto_now_add = True, editable = False)

    def is_pending(self):
        """Returns true if the application is still pending else returns false."""
        return self.status == self.PENDING
    
    def is_accepted(self):
        """Returns true if the application is accepted else returns false."""
        return self.status == self.ACCEPTED

    def is_rejected(self):
        """Returns true if the application is rejected else returns false."""
        return self.status == self.REJECTED

    def cannot_be_created(self):
        """Returns true if a given user already has a 
        non-rejected application in a club else return false."""
        return ((user_has_pending_application_to_the_same_club(self.user, self.club)) or
                (user_has_accepted_application_to_the_same_club(self.user, self.club)))

    def save(self, *args, **kwargs):
        """Saves the application to the database."""
        if (self.status == self.PENDING) and (self.cannot_be_created()):
            raise IntegrityError("User can have only one panding/accepted application to the same club")
        super().save(*args, **kwargs)

    class Meta:
        """Model options, provides an ordering to the applications."""
        ordering = ["-created_at"]

def user_has_pending_application_to_the_same_club(user, club):
    """Return true if a user already has pending application in a given
     club else returns false."""
    return (Application.objects.filter(user = user, status = Application.PENDING, club = club)).exists()

def user_has_accepted_application_to_the_same_club(user, club):
    """Return true if a user already has an accepted application in a given
     club else returns false."""
    return (Application.objects.filter(user = user, status = Application.ACCEPTED, club = club)).exists()