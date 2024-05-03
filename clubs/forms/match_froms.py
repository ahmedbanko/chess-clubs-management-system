"""Forms to create and update matches between two memebers of the same club."""

from django import forms
from clubs.models import Match, User, Membership
from datetime import datetime
import pytz

class CreateMatchForm(forms.ModelForm):
    """Form enabling officers to create a new match."""
    
    class Meta:
        """Form options."""
        model = Match
        fields = ['player_1', 'player_2', 'location', 'date_time']
        widgets = {'date_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S',
         attrs={'class': 'datetimepicker', 'placeholder': 'yyyy-MM-dd HH:mm'})}

    def __init__(self, club, *args, **kwargs):
        """Initialises form choices."""
        super(CreateMatchForm, self).__init__(*args, **kwargs)
        membership = Membership.objects.filter(club=club)
        queryset = User.objects.filter(membership__in = membership)
        self.fields['player_1'].queryset = queryset
        self.fields['player_2'].queryset = queryset

    def save(self, club):
        """Save and returns a match object if possible."""
        super().save(commit=False)
        match = Match.objects.create(
            player_1 = self.cleaned_data.get('player_1'),
            player_2 = self.cleaned_data.get('player_2'),
            club = club,
            location = self.cleaned_data.get('location'),
            date_time =self.cleaned_data.get('date_time')
        )
        return match 

    def is_valid(self):
        """Validates the form inputs and returns true if valid."""
        if super().is_valid():
           
            player1and2_identical = self._are_players_identiacal()
            match_conflicts = self.players_have_conflicting_matches(self)
            
            if player1and2_identical:
                self.add_error('player_2', 'Both players cannot be the same!')
                return False
            elif match_conflicts:
                self.add_error('date_time', 'One or both players have a schedulled match at this date/time!')
                return False
            elif self.is_invalid_date():
                self.add_error('date_time', 'Date/time must be in future!')
                False
            else:
                return True

        return False

    def _are_players_identiacal(self):
        """Return true if player 1 and two are identical."""
        return self.cleaned_data.get('player_1') == self.cleaned_data.get('player_2')

    def is_invalid_date(self):
        """Returns true if the date given is before the current date."""
        try:
            utc = pytz.UTC
            input_date_time = self.cleaned_data.get('date_time')
            if input_date_time <= utc.localize(datetime.today()):
                return True
            else:
                return False
        except:
            return True

    def players_have_conflicting_matches(self, form):
        """Check if players has a scheduled match at the new match date/time."""
        player_1 = form.cleaned_data.get('player_1')
        player_2 = form.cleaned_data.get('player_2')
        date_time = form.cleaned_data.get('date_time')
        a = Match.objects.filter(player_1=player_1, date_time=date_time).exists() 
        b = Match.objects.filter(player_2=player_1, date_time=date_time).exists()  
        c = Match.objects.filter(player_1=player_2, date_time=date_time).exists()  
        d = Match.objects.filter(player_2=player_2, date_time=date_time).exists()
        return a or b or c or d

class UpdateMatchOutcomeForm(forms.ModelForm):
    """Form enabling officers to update an outcome of a match."""
    choices = Match.STATUS[1:]
    status = forms.ChoiceField(choices = choices)

    class Meta:
        """Form options."""
        model = Match
        fields = ['status']

    def save(self, match_id):
        """Saves the given status of the match."""
        super().save(commit=False)
        match = Match.objects.get(id = match_id)
        match.status = self.cleaned_data.get('status')
        match.save()
        return match
