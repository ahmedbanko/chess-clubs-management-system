"""Views for user matches."""

from clubs.models import Match
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from clubs.views.helpers import ChangeMatchOutcome

class UserMatchesView(LoginRequiredMixin, TemplateView):
    """ View for displaying the user's list of matches """
    template_name = "match_templates/user_matches.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        matches = Match.objects.filter(player_1=self.request.user) | Match.objects.filter(player_2=self.request.user)
        context['upcoming_matches'] = matches.filter(status=Match.PENDING).order_by('-date_time')
        context['previous_matches'] = matches.exclude(status=Match.PENDING).order_by('-date_time')
        context['wins'] = len(Match.objects.filter(player_1=self.request.user, status=Match.PLAYER1)) + len(
            Match.objects.filter(player_2=self.request.user, status=Match.PLAYER2))
        context['losses'] = len(Match.objects.filter(player_2=self.request.user, status=Match.PLAYER1)) + len(
            Match.objects.filter(player_1=self.request.user, status=Match.PLAYER2))
        context['draws'] = len(matches.filter(status=Match.DRAW))
        return context


class ForfeitMatchView(LoginRequiredMixin, ChangeMatchOutcome):
    """ View for forfeiting a match """

    http_method_names = ['get', 'post']

    def handle(self, request, *args, **kwargs):
        """Handle if the match can be forfeited"""
        if not self.match.is_pending():
            messages.add_message(request, messages.INFO, 'This match already has a result')
            return self.redirect()

    def get(self, request, *args, **kwargs):
        """ Forfeit match """
        if self.request.user == self.match.player_1:
            self.match.status = Match.PLAYER2
            self.match.save()
            messages.add_message(request, messages.SUCCESS, 'Match has been successfully forfeited')
        elif self.request.user == self.match.player_2:
            self.match.status = Match.PLAYER1
            self.match.save()
            messages.add_message(request, messages.SUCCESS, 'Match has been successfully forfeited')
        else:
            messages.add_message(request, messages.ERROR, 'You cannot forfeit this match')
        return self.redirect()

    def redirect(self):
        return redirect('club_home', self.kwargs['club_id'])
