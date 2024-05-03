"""Views that deal with the user account."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from clubs.forms import UserForm, PasswordForm
from django.contrib import messages
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from clubs.views import login_prohibited
from django.views.generic.base import View
from clubs.models import User, Club
from django.contrib.auth.mixins import LoginRequiredMixin

"""View of the change profile details page."""
@login_required
def profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('dashboard')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'account_templates/profile.html', {'form': form})


"""View of the change password page."""
@login_required
def password(request):
    current_user = request.user
    valid_current_password = True
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('dashboard')
            else:
                valid_current_password = False
        if(not valid_current_password):
            form.add_error('password', 'Incorrect current password!')  
    else:
        form = PasswordForm()     
    return render(request, 'account_templates/password.html', {'form': form})


class PasswordResetView(auth_views.PasswordResetView):
    """View that handles password reset."""
    form_class = PasswordResetForm
    template_name = 'account_templates/password_reset.html'

    @method_decorator(login_prohibited)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """View that handles password reset confirmation."""

    template_name = 'account_templates/password_reset_confirm.html'

    @method_decorator(login_prohibited)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """View for password reset completion."""

    template_name = 'account_templates/password_reset_complete.html'

    @method_decorator(login_prohibited)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    """View for password reset that is done."""

    template_name = 'account_templates/password_reset_done.html'

    @method_decorator(login_prohibited)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CloseAccountView(View):
    """View that handles account closure."""

    http_method_names = ['get', 'post']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_owner():
            messages.add_message(request, messages.INFO, 'Cannot close account if you are an owner of one or more clubs. Transfer ownership or delete your clubs before closing your account')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Display close account template."""
        return render(request, 'account_templates/close_account.html', {'user': request.user.username})

    def post(self, request, *args, **kwargs):
        """Handle account closure attempt."""
        user = User.objects.get(username=request.user.username)
        user.delete()
        return redirect('home')
