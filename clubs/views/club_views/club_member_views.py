"""Views that handle members in the club."""

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import TemplateView, View
from clubs.models import User, Application, Match, Membership, Club
from django.shortcuts import redirect, render
from django.contrib import messages
from clubs.views.helpers import MembershipRequiredMixin, OfficerRequiredMixin, OwnerRequiredMixin

class MembersListView(MembershipRequiredMixin, TemplateView):
	"""View that shows a list of all members."""
	template_name = "club_templates/members_list.html"

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args,**kwargs)
		club = Club.objects.get(id=self.kwargs['club_id'])
		context['members'] = Membership.objects.filter(club=club).order_by('user')
		return context


class ShowUserView(MembershipRequiredMixin, View):    
    """View that shows individual user details."""

    def get(self, request, *args, **kwargs):
        """Display user template, redirect to member list if user does not exist"""
        try:
            target_user = User.objects.get(id=self.kwargs['user_id'])
            club = Club.objects.get(id=self.kwargs['club_id'])
            user = Membership.objects.get(user=target_user, club=club).user
            personal_statement = (Application.objects.get(user=user, club=club, status=Application.ACCEPTED)).personal_statement
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'That user does not exist.')
            return redirect('members_list', self.kwargs['club_id'])
        else:
            matches =  Match.objects.filter(club=club, player_1=user) | Match.objects.filter(club=club, player_2 = user)

            context = {
                'user': user,
                'personal_statement' : personal_statement,
                'logged_in_user_is_member' : self.request.user.is_member_of(club),
                'logged_in_user_is_officer' : self.request.user.is_officer_of(club),
                'logged_in_user_is_owner' : self.request.user.is_owner_of(club),
                'shown_user_is_member' : user.is_member_of(club),
                'shown_user_is_officer' : user.is_officer_of(club),
                'shown_user_is_owner' : user.is_owner_of(club),
                'upcoming_matches' : matches.filter(status = Match.PENDING),
                'previous_matches' : matches.exclude(status = Match.PENDING),
                'wins' : len(matches.filter(player_1 = user, status = Match.PLAYER1)) + len(matches.filter(player_2 = user, status = Match.PLAYER2)),
                'losses' : len(matches.filter(player_2 = user, status = Match.PLAYER1)) + len(matches.filter(player_1 = user, status = Match.PLAYER2)),
                'draws' : len(matches.filter(status = Match.DRAW)),
                'club_id' : self.kwargs['club_id'],
            }
            return render(request, 'club_templates/show_user.html', context)

class ChangeMemberPermissions(View):
    """Class to extend for views that change member status."""
    def post(self, request, *args, **kwargs):
        try:
            target_user = User.objects.get(id=self.kwargs['user_id'])
            club = Club.objects.get(id=self.kwargs['club_id'])
            member = Membership.objects.get(user=target_user, club=club)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'The provided ID does not match any existing members!')
            return redirect('members_list', self.kwargs['club_id'])
        else:
            self.handle(request, target_user, club, member, *args, **kwargs)
        return redirect('members_list', self.kwargs['club_id'])

class PromoteMemberView(OfficerRequiredMixin, ChangeMemberPermissions):
    """View that handles promote member."""

    def handle(self, request, target_user, club, member, *args, **kwargs):
        """Promote member to officer."""
        if target_user.is_member_of(club):
            member.role = Membership.OFFICER
            member.save()
            messages.add_message(request, messages.SUCCESS, 'Member promoted!')
        else:
            messages.add_message(request, messages.ERROR, 'An error occured while trying to promote!')

class DemoteOfficerView(OwnerRequiredMixin, ChangeMemberPermissions):
    """View that handles demote officer."""

    def handle(self, request, target_user, club, officer, *args, **kwargs):
        """Demote officer to member."""
        if target_user.is_officer_of(club):
            officer.role = Membership.MEMBER
            officer.save()
            messages.add_message(request, messages.SUCCESS, 'Officer demoted!')
        else:
            messages.add_message(request, messages.ERROR, 'An error occured while trying to demote!')

class DeleteMemberView(OfficerRequiredMixin, ChangeMemberPermissions):
    """View that handles delete member from a club."""

    def handle(self, request, target_user, club, officer, *args, **kwargs):
        """Delete a member from the club."""
        if target_user.is_officer_of(club) and (not request.user.is_owner_of(club)): 
            messages.add_message(request, messages.SUCCESS, 'You are not authorized to procced!')
        elif not target_user.is_owner_of(club):
            application = Application.objects.get(user=target_user, club=club, status=Application.ACCEPTED)
            application.status = Application.REJECTED
            application.save()
            Membership.objects.get(user=target_user, club=club).delete()
            messages.add_message(request, messages.SUCCESS, 'Member Deleted!')
        else:
            messages.add_message(request, messages.ERROR, 'An error occured while trying to deleted this member!')

class TransferOwnershipView(OwnerRequiredMixin, View):
    """View that handles transferring ownership of a club."""

    def get(self, request, *args, **kwargs):
        """Handle get request for transferring an ownership."""
        try:
            club = Club.objects.get(id=self.kwargs['club_id'])
            target_user = User.objects.get(id=self.kwargs['user_id'])
            user = Membership.objects.get(user=target_user, club=club).user      
            owner = Membership.objects.get(user=request.user, club=club, role=Membership.OWNER)
            new_owner = Membership.objects.get(user_id=self.kwargs['user_id'], club=club)  
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'That user does not exist.')
            return redirect('club_home', club_id=self.kwargs['club_id'])
        else:
            if owner == new_owner:
                messages.error(request, 'You are already the owner of the club.')
                return redirect('club_home', club_id=self.kwargs['club_id'])

            context = {
                'user_id': self.kwargs['user_id'],
                'user': user,
                'logged_in_user_is_member' : self.request.user.is_member_of(club),
                'logged_in_user_is_officer' : self.request.user.is_officer_of(club),
                'logged_in_user_is_owner' : self.request.user.is_owner_of(club),
                'club_id' : self.kwargs['club_id'],
            }

            return render(self.request, 'club_templates/transfer_ownership.html', context)

    def post(self, request, *args, **kwargs):
        """Transfer ownership to new owner."""
        try:
            club = Club.objects.get(id=self.kwargs['club_id'])
            owner = Membership.objects.get(user=request.user, club=club, role=Membership.OWNER)
            new_owner = Membership.objects.get(user_id=self.kwargs['user_id'], club=club)      
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'That user does not exist.')
            return redirect('club_home', club_id=self.kwargs['club_id'])
        else:
            if owner == new_owner:
                messages.error(request, 'You are already the owner of the club.')
                return redirect('club_home', club_id=self.kwargs['club_id'])
            else:
                owner.role = Membership.OFFICER
                owner.save()
                new_owner.role = Membership.OWNER
                new_owner.save()
                return redirect('club_home', club_id=self.kwargs['club_id'])
