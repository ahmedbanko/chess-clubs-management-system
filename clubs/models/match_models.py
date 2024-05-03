"""The models that encapsulate a match between two users in the same club."""

from django.db import models
from clubs.models import User, Club
from django.db.utils import IntegrityError
from datetime import datetime
import pytz

class Match(models.Model):
    """Match model used for creating a match between two users of the same club."""
    player_1 = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        blank = False,
        null = False,
        related_name = 'player_1',
    )

    player_2 = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        blank = False,
        null = False,
        related_name = 'player_2',
    )

    club = models.ForeignKey(
        Club,
        on_delete = models.CASCADE,
        blank = False,
        null = False,
    )

    location = models.CharField(unique = False, max_length = 100, blank = False)
    date_time = models.DateTimeField(blank = False)

    # Status options for match outcomes
    PENDING = "Pending"
    PLAYER1 = "Player1"
    PLAYER2 = "Player2"
    DRAW = "Draw"
    CANCELLED = "Cancelled"

    STATUS = [
        (PENDING, "Pending"),
        (PLAYER1, "Player 1's Win"),
        (PLAYER2, "Player 2's Win"),
        (DRAW, "Draw"),
        (CANCELLED, "Cancelled"),
    ]

    status = models.CharField(max_length = 15, choices = STATUS, default = PENDING, blank = False)

    def is_pending(self):
        """Returns true if match is pending else returns false."""
        return self.status == self.PENDING
    
    def is_player_1_win(self):
        """Returns true if match player_1 is the winner of the match 
        else returns false."""
        return self.status == self.PLAYER1

    def is_player_2_win(self):
        """Returns true if match player_2 is the winner of the match 
        else returns false."""
        return self.status == self.PLAYER2

    def is_draw(self):
        """Returns true if match ended in a draw else returns false."""  
        return self.status == self.DRAW

    def is_cancelled(self):
        """Returns true if the match was cancelled else returns false."""  
        return self.status == self.CANCELLED

    def is_overdue(self):
        """Returns true if the match is overdue else returns false."""
        utc = pytz.UTC
        current_time = utc.localize(datetime.today()).strftime("%Y-%m-%d %H:%M:%S")
        return current_time >= str(self.date_time)

    def save(self, *args, **kwargs):
        """Saves the match into the database or generates errors if any."""
        if (not self.members_from_same_club() or (self.player_1 is self.player_2) or self.is_a_duplicate()) and self.is_pending():
            raise IntegrityError("Matches are only for two distinct members who must be in the same club!")
        super().save(*args, **kwargs)

    class Meta:
        """Model options, provides ordering for our matches."""
        ordering = ["-date_time"]

    def members_from_same_club(self):
        """Check if both players are in the same club."""
        return self.is_in_club(self.player_1, self.club) and self.is_in_club(self.player_2, self.club)

    def is_in_club(self, player, club):
        """Check if a given player is in a club."""
        return player.is_member_of(club) or player.is_officer_of(club) or player.is_owner_of(club)

    def is_a_duplicate(self):
        """Check if a match has already been created with identical data."""
        return (Match.objects.filter(
            player_1=self.player_1,
            player_2=self.player_2,
            club=self.club,
            location=self.location,
            date_time=self.date_time,
            status = Match.PENDING)
        ).exists()  
