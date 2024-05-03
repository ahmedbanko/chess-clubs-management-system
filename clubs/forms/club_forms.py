"""Form to create a new club."""

from django import forms
from clubs.models import Club

class CreateClubForm(forms.ModelForm):
    """Form enabling users to create a new club."""
   
    class Meta:
        """Form options."""
        model = Club
        fields = ['name', 'location', 'description']
        widgets = { 'description': forms.Textarea()}

    def get_club(self):
        """Returns newly created club if possible."""
        club = None
        if self.is_valid():
            club = Club.objects.create(
                name = self.cleaned_data.get('name'),
                location = self.cleaned_data.get('location'),
                description =self.cleaned_data.get('description')
            )
        return club    