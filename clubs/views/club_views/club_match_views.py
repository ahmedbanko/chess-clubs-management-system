"""Views that deal with club matches."""

from django.shortcuts import render, redirect
from clubs.forms import CreateMatchForm
from clubs.models import  Club, Match
from django.views import View
from clubs.views.helpers import ChangeMatchOutcome, OfficerRequiredMixin
from django.contrib import messages
from clubs.forms import UpdateMatchOutcomeForm

class CreateMatchView(OfficerRequiredMixin, View):
    """Create new match view class."""

    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        """Dispatch as normal."""
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Render the form for create match."""
        self.club = (Club.objects.get(id=kwargs['club_id']))
        self.form = CreateMatchForm(self.club)
        return self.render(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle match creation."""
        self.club = (Club.objects.get(id=kwargs['club_id']))
        self.form = CreateMatchForm(self.club, data=self.request.POST)
        if self.form.is_valid():
            self.form.save(self.club)
            messages.add_message(request, messages.SUCCESS, 'Match has been created')
            return redirect('club_home', kwargs['club_id'])
        else:
            return self.render(*args, **kwargs)


    def render(self, *args, **kwargs):
        """Display create match template."""
        context = {
                'logged_in_user_is_officer' : self.request.user.is_officer_of(self.club),
                'logged_in_user_is_owner' : self.request.user.is_owner_of(self.club),
                'form': self.form, 
                'club_id': self.kwargs['club_id']
            }
        return render(self.request, 'club_templates/create_match.html', context)

class UpdateMatchOutcomeView(OfficerRequiredMixin, ChangeMatchOutcome):
    """Update match with outcome."""

    http_method_names = ['get', 'post']

    def handle(self, request, *args, **kwargs):
        """Handle if match outcome can be updated"""
        if not self.match.is_overdue() or not self.match.is_pending():
            messages.add_message(request, messages.INFO, 'This match has either not been played yet or has alredy a result set')
            return self.redirect()

    def get(self, request, *args, **kwargs):
        """Display update match form."""
        self.form = UpdateMatchOutcomeForm()
        return self.render()
 
    def post(self, request, *args, **kwargs):
        """Handle update match attempt."""
        self.form = UpdateMatchOutcomeForm(request.POST)
        if self.form.is_valid():
            post = self.form.save(self.match.id)
            messages.add_message(request, messages.SUCCESS, 'Match outcome has been updated')
            return self.redirect()
        else:
            messages.add_message(request, messages.ERROR, 'Match outcome has invalid format')
        return self.render()

    def render(self):
        """Render update match form with correct match details."""
        club = Club.objects.get(id=self.kwargs['club_id'])

        context = {
            'match': self.match,
            'form': self.form,
            'club_id': self.kwargs['club_id'],
            'logged_in_user_is_officer' : self.request.user.is_officer_of(club),
            'logged_in_user_is_owner' : self.request.user.is_owner_of(club),
        }
        
        return render(self.request, 'club_templates/update_match.html', context)

    def redirect(self):
        """Redirect to club home."""
        return redirect('club_home', self.kwargs['club_id'])

class CancelMatchView(OfficerRequiredMixin, ChangeMatchOutcome):
    """View for cancelling a match."""

    http_method_names = ['get', 'post']

    def handle(self, request, *args, **kwargs):
        """Handles if match can be cancelled."""
        if not self.match.is_pending():
            messages.add_message(request, messages.INFO, 'Cannot cancel a match that already has an outcome')
            return self.redirect()

    def get(self, request, *args, **kwargs):
        """Cancel match."""
        return self.cancel_match(*args, **kwargs)
 
    def post(self, request, *args, **kwargs):
        """Cancel match."""
        return self.cancel_match(*args, **kwargs)

    def cancel_match(self, *args, **kwargs):
        self.match.status = Match.CANCELLED
        self.match.save()
        return self.redirect()

    def redirect(self):
        return redirect('club_home', self.kwargs['club_id'])
