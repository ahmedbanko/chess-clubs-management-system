"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('sign_up/', views.sign_up, name="sign_up"),
    path('log_in/', views.LogInView.as_view(), name="log_in"),
    path('dashboard/', views.ClubListView.as_view(), name="dashboard"),
    path('applications/', views.ApplicationListView.as_view(), name="applications"),
    path('log_out/', views.log_out, name='log_out'),
    path('application/', views.NewApplicationView.as_view(), name="application"),
    path('application/<int:club_id>', views.NewApplicationView.as_view(), name="application"),
    path('close_account/', views.CloseAccountView.as_view(), name="close_account"),
    path('password/', views.password, name='password'),
    path('profile/', views.profile, name='profile'),
    path('applications/cancel_application/<int:application_id>', views.CancelApplicationView.as_view(), name='cancel_application'),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('create_club/', views.CreateClubView.as_view(), name="create_club"),
    path('club/<int:club_id>', views.ClubHomeView.as_view(), name="club_home"),
    path('club/<int:club_id>/members/', views.MembersListView.as_view(), name='members_list'),
    path('club/<int:club_id>/applications/', views.ClubApplicationsView.as_view(), name="club_application_list"),
    path('club/<int:club_id>/accept_application/<int:application_id>', views.AcceptApplicationView.as_view(), name='accept_application'),
    path('club/<int:club_id>/reject_application/<int:application_id>', views.RejectApplicationView.as_view(), name='reject_application'),   
    path('club/<int:club_id>/user/<int:user_id>', views.ShowUserView.as_view(), name='show_user'),
    path('club/<int:club_id>/promote_member/<int:user_id>', views.PromoteMemberView.as_view(), name='promote_member'),
    path('club/<int:club_id>/demote_officer/<int:user_id>', views.DemoteOfficerView.as_view(), name='demote_officer'),
    path('club/<int:club_id>/delete_member/<int:user_id>', views.DeleteMemberView.as_view(), name='delete_member'),
    path('club/<int:club_id>/transfer_ownership/<int:user_id>', views.TransferOwnershipView.as_view(), name="transfer_ownership"),   
    path('leave_club/<int:club_id>', views.LeaveClubView.as_view(), name='leave_club'),
    path('club/<int:club_id>/delete_club', views.DeleteClubView.as_view(), name="delete_club"),
    path('club/<int:club_id>/create_match', views.CreateMatchView.as_view(), name="create_match"),
    path('my_matches/', views.UserMatchesView.as_view(), name='user_matches'),
    path('club/<int:club_id>/update_match/<int:match_id>', views.UpdateMatchOutcomeView.as_view(), name="update_match"),
    path('club/<int:club_id>/forfeit_match/<int:match_id>', views.ForfeitMatchView.as_view(), name='forfeit_match'),
    path('club/<int:club_id>/cancel_match/<int:match_id>', views.CancelMatchView.as_view(), name="cancel_match"),

]

