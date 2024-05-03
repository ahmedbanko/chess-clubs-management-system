"""Forms to send an application to a given club."""

from django import forms
from clubs.models import Application, Club

class MyModelChoiceField(forms.ModelChoiceField):
    """A choice field that contains the possible list of clubs."""
    def label_from_instance(self, club):
        return club.name

class ApplicationForm(forms.ModelForm):
    """Form enabling users to apply to a club."""

    club = MyModelChoiceField(queryset=Club.objects.all(), to_field_name = "name")

    class Meta:
        """Form options."""
        model = Application
        fields = ['club', 'personal_statement']
        widgets = {'personal_statement': forms.Textarea()}

    def save(self, userIn):
        """Returns newly created application if possible."""
        super().save(commit=False)
        application = Application.objects.create(
            personal_statement = self.cleaned_data.get('personal_statement'),
            club = self.cleaned_data.get('club'),
            user = userIn
        )
        return application
