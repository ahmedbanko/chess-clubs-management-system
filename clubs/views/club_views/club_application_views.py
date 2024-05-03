"""Views that deal with applications for a club."""

from django.views.generic.base import TemplateView, View
from clubs.models import Application, Membership, Club
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from clubs.views.helpers import OfficerRequiredMixin

class ClubApplicationsView(OfficerRequiredMixin, TemplateView):
    """View to display pending applications for a club."""

    template_name = "club_templates/club_application_list.html"

    def get_context_data(self, *args, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(*args,**kwargs)
        club = Club.objects.get(id=self.kwargs['club_id'])
        context['applications'] = Application.objects.filter(club=club, status=Application.PENDING)
        return context

class ChangeApplication(OfficerRequiredMixin, View):
    """Class to extend for views that change application status."""

    def post(self, request, *args, **kwargs):
        """Handle the acceptence of the application."""
        try:
            application = Application.objects.get(id=kwargs['application_id'], club=kwargs['club_id'])
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'That application does not exist')
            return redirect('club_application_list', kwargs['club_id'])
        else:
            self.handle(application)
        return redirect('club_application_list', kwargs['club_id'])

class AcceptApplicationView(ChangeApplication):
    """View that handles application acceptence."""

    def handle(self, application):
        """ Sets the application status to accepted if it is pending. """
        if application.status == Application.PENDING:
            application.status = Application.ACCEPTED
            application.save()
            Membership.objects.create(user=application.user, club=application.club)
            messages.add_message(self.request, messages.SUCCESS, 'Application accepted!')
        else:
            messages.add_message(self.request, messages.ERROR, 'You cannot accept that application!')

class RejectApplicationView(ChangeApplication):
    """View that handles application rejecting."""

    def handle(self, application):
        """Sets the application status to rejected if it is pending."""
        if application.status == Application.PENDING:
            application.status = Application.REJECTED
            application.save()
            messages.add_message(self.request, messages.SUCCESS, 'Application rejected!')
        else:
            messages.add_message(self.request, messages.ERROR, 'You cannot reject that application!')
