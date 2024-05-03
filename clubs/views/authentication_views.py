"""Views that deal with user authentication."""

from clubs.forms import LogInForm, SignUpForm
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from clubs.views.helpers import login_prohibited
from clubs.views.helpers import LoginProhibitedMixin


class LogInView(LoginProhibitedMixin, View):
    """View that handles log in."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Display log in template."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempts."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or 'home'
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, 'The credentials provided were invalid!')
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""
        form = LogInForm()
        return render(self.request, 'authentication_templates/log_in.html', {'form': form, 'next': self.next})


@login_prohibited
def sign_up(request):
    """The sign up view used by the user to register for an account."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'authentication_templates/sign_up.html', {'form': form})


def log_out(request):
    """The log out view."""
    logout(request)
    return redirect('home')
