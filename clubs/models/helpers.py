"""Helper classes for the rest of the models."""

from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def create_user(self, email, password=None, **kwargs):
        """Create and save a regular User with the given email, username and password."""
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        """Create and save a SuperUser with the given email and password."""
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self._create_user(email, password, username=email[:email.find("@")], **kwargs)

    def _create_user(self, email, password, **kwargs):
        """Create and save a User with the given email and password."""
        if not email or not password:
            raise ValueError('The given email and password must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
