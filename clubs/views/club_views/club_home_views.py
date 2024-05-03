"""Views for the club home page."""

from django.db.models import Q
from django.views.generic.base import TemplateView
from clubs.models import Club, Membership, Match
from clubs.views.helpers import MembershipRequiredMixin

class ClubHomeView(MembershipRequiredMixin, TemplateView):
    """View that displays the club home page."""
    template_name = "home_templates/club_home.html"

    def get_context_data(self, *args, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(*args, **kwargs)
        context['club'] = Club.objects.get(id=self.kwargs['club_id'])
        membership = Membership.objects.filter(role=Membership.OWNER, user=self.request.user)
        context['owned_clubs'] = Club.objects.filter(membership__in=membership)
        context['matches'] = Match.objects.filter(club=context['club'])
        return context
