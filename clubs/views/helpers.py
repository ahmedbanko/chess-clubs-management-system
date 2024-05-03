"""Mixins, decorators, helper methods and helper classes for rest of the views."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib import messages
from clubs.models import Club, Match
from django.views import View
from django.core.exceptions import ObjectDoesNotExist

def login_prohibited(view_function):
    """Modifies a view function so that when the user is not logged in they are redirected."""

    def modified_view_function(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function

class LoginProhibitedMixin:
    @method_decorator(login_prohibited)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class PermissionContextMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['logged_in_user_is_member'] = _is_member(self.request, self.kwargs['club_id'])
        context['logged_in_user_is_officer'] = _is_officer(self.request, self.kwargs['club_id'])
        context['logged_in_user_is_owner'] = _is_owner(self.request, self.kwargs['club_id'])
        context['club_id'] = self.kwargs['club_id']
        return context

class MembershipRequiredMixin(PermissionContextMixin):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            Club.objects.get(id=kwargs['club_id'])
        except:
            messages.add_message(request, messages.ERROR, 'That club does not exist!')
            return redirect('dashboard')

        if not (_is_member(request, self.kwargs['club_id'])):
            message = 'You are not in that club please apply or wait for application approval first!'
            messages.add_message(request, messages.ERROR, message)
            return redirect(settings.REDIRECT_URL_WHEN_MEMBERSHIP_REQUIRED)
        else:
            return super().dispatch(request, *args, **kwargs)

class OfficerRequiredMixin(PermissionContextMixin):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            Club.objects.get(id=kwargs['club_id'])
        except:
            messages.add_message(request, messages.ERROR, 'That club does not exist!')
            return redirect('dashboard')

        if not (_is_officer(request, self.kwargs['club_id'])):
            messages.add_message(request, messages.ERROR, 'You need to be an officer to access that page!')
            return redirect(settings.REDIRECT_URL_WHEN_PERMISSIONS_ARE_NOT_HIGH_ENOUGH, club_id=self.kwargs['club_id'])
        else:
            return super().dispatch(request, *args, **kwargs)

class OwnerRequiredMixin(PermissionContextMixin):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            Club.objects.get(id=kwargs['club_id'])
        except:
            messages.add_message(request, messages.ERROR, 'That club does not exist!')
            return redirect('dashboard')

        if not _is_owner(request, self.kwargs['club_id']):
            messages.add_message(request, messages.ERROR, 'You need to be the owner to access that page!')
            return redirect(settings.REDIRECT_URL_WHEN_PERMISSIONS_ARE_NOT_HIGH_ENOUGH, club_id=self.kwargs['club_id'])
        else:
            return super().dispatch(request, *args, **kwargs)

class ChangeMatchOutcome(View):
    """Class to extend for views changing the outcome of a match."""

    def dispatch(self, request, *args, **kwargs):
        """Redirect to club home of match cannot be changed, dispatch as normal otherwise."""
        self.kwargs = kwargs
        try:
            self.match = Match.objects.get(id=kwargs['match_id'])
            self.handle(request, *args, **kwargs)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'That match does not exist')
            return self.redirect()
        if self.match.club.id == kwargs['club_id']:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'You are not in the right club to access this match')
            return self.redirect()

def _is_member(request, club_id):
    return request.user.is_member_of(Club.objects.get(id=club_id)) or _is_officer(request, club_id)

def _is_officer(request, club_id):
    return request.user.is_officer_of(Club.objects.get(id=club_id)) or _is_owner(request, club_id)

def _is_owner(request, club_id):
    return request.user.is_owner_of(Club.objects.get(id=club_id))
