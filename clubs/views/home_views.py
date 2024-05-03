"""Views for the website's home page."""

from django.shortcuts import render
from clubs.views.helpers import login_prohibited
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView, View
from clubs.models import Application, Membership, Club, User
from django.shortcuts import redirect, render
from django.contrib import messages
from clubs.views.helpers import MembershipRequiredMixin, OwnerRequiredMixin
from clubs.forms import CreateClubForm
from django.core.mail import EmailMessage


@login_prohibited
def home(request):
    """Home view used for when the user enter the application."""
    return render(request, 'account_templates/home.html')


class ClubListView(LoginRequiredMixin, TemplateView):
    """Club list view."""
    template_name = 'account_templates/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        membership = Membership.objects.filter(user=self.request.user)
        context['my_clubs'] = Club.objects.filter(membership__in=membership)
        context['clubs'] = Club.objects.exclude(membership__in=membership)
        membership = Membership.objects.filter(role=Membership.OWNER, user=self.request.user)
        context['owned_clubs'] = Club.objects.filter(membership__in=membership)
        return context

class LeaveClubView(MembershipRequiredMixin, View):
    """View that handles leave club"""

    def get(self, request, *args, **kwargs):
        return render(request, 'home_templates/leave_club.html', {'club_id': self.kwargs['club_id']})

    def post(self, request, *args, **kwargs):
        """Removes user from club"""
        club = Club.objects.get(id=self.kwargs['club_id'])
        member = Membership.objects.get(user=request.user, club=club)
        if member.role == Membership.OWNER:
            messages.warning(request, "Owners are not allowed to leave their club.")
            return redirect('club_home', self.kwargs['club_id'])
        else:
            application = Application.objects.get(status=Application.ACCEPTED, club=club, user=member.user)
            application.status = Application.REJECTED
            application.save()
            member.delete()
            messages.success(request, "You have successfully left the club")
            return redirect('dashboard')

class CreateClubView(LoginRequiredMixin, View):
    """View that handles creating a new club."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Display create club template."""
        self.next = request.GET.get('next') or 'dashboard'
        return self.render()

    def post(self, request):
        """Handle create club attempts."""
        form = CreateClubForm(request.POST)
        self.next = request.POST.get('next') or 'dashboard'
        club = form.get_club()
        if club is not None:
            owner = request.user
            Application.objects.create(user=owner, club=club, personal_statement="Club owner",
                                       status=Application.ACCEPTED).save()
            Membership.objects.create(user=owner, club=club, role=Membership.OWNER).save()
            return redirect('club_home', club.id)
        """If creating a club was unsuccesfull"""
        messages.add_message(self.request, messages.ERROR, 'This club name is taken!')
        form = CreateClubForm()
        return self.render()

    def render(self):
        """Render create club template with blank form."""
        form = CreateClubForm()
        return render(self.request, 'home_templates/create_club.html', {'form': form, 'next': self.next})


class DeleteClubView(OwnerRequiredMixin, View):
    """View that handles deleteing of a club."""

    def get(self, request, *args, **kwargs):
        """Display delete club template."""
        club = Club.objects.get(id=kwargs['club_id'])
        return render(request, 'home_templates/delete_club.html', {'club': club})

    def post(self, request, *args, **kwargs):
        """Handle delete club attempt."""
        club = Club.objects.get(id=kwargs['club_id'])
        self.send_emails(club)
        club.delete()
        messages.add_message(self.request, messages.SUCCESS, 'You have successfully deleted your club')
        return redirect('dashboard')

    def send_emails(self, club):
        """Send email about club deletion"""
        membership = Membership.objects.filter(club = club)
        members = User.objects.filter(membership__in = membership)

        emails = []
        for member in members:
            emails.append(member.email)
        email = EmailMessage(
            'Club Deleted',
            f'You are recieving this email because the {club.name} club was recently deleted.'
            '\nAs a former member of this club, you will no longer be able to access its home page.'
            '\nWe are sorry if this causes any inconveniences.'
            '\n'
            '\nThe Polecat Chess Team',
            'polecatchess@gmail.com',
            bcc=emails
        )
        email.send()
