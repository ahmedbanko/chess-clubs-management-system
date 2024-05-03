"""Views that deal with user's applications."""

from clubs.models import Application, Club
from clubs.forms import ApplicationForm
from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist


class NewApplicationView(LoginRequiredMixin, View):
    """Create new application view class."""

    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get application form."""
        try:
            club_name = (Club.objects.get(id=kwargs['club_id'])).name
            self.form = ApplicationForm(initial={'club': club_name})
        except:
            self.form = ApplicationForm()
        return self.render()

    def post(self, request, *args, **kwargs):
        """Handle new application attempt."""
        self.form = ApplicationForm(request.POST)
        user = request.user
        for application in Application.objects.filter(user=user):
            if (application.club.name == request.POST.get('club')) and (
                    application.is_pending() or application.is_accepted()):
                messages.add_message(request, messages.ERROR, 'Application for this club has already been submitted')
                self.form = ApplicationForm()
                return self.render()
        if self.form.is_valid():
            self.form.save(user)
            messages.add_message(request, messages.SUCCESS, 'Application has been submitted')
            return redirect('applications')
        else:
            messages.add_message(request, messages.ERROR, 'Application has invalid format')
        return self.render()

    def render(self):
        return render(self.request, 'application_templates/new_application.html', {'form': self.form})


class ApplicationListView(LoginRequiredMixin, ListView):
    """View that displays user's list of applications."""
    model = Application
    template_name = "application_templates/application_list.html"
    context_object_name = 'applications'

    def get_queryset(self):
        """Return the logged in user's applications."""
        return Application.objects.filter(user=self.request.user)


class CancelApplicationView(LoginRequiredMixin, View):
    """Cancel application view class."""

    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Cancel application."""
        return self.cancel_application(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Cancel application."""
        return self.cancel_application(*args, **kwargs)

    def cancel_application(self, *args, **kwargs):
        try:
            application = Application.objects.get(id=kwargs['application_id'], user=self.request.user)
            if (application.is_pending()):
                application.delete()
                return redirect('applications')
            else:
                messages.add_message(self.request, messages.INFO,
                                     'Cannot cancel application that has already been processed.')
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.INFO,
                                 'The application you are trying to cancel does not exist.')
        applications_list = Application.objects.filter(user=self.request.user)
        return render(self.request, 'application_templates/application_list.html', {'applications': applications_list})
