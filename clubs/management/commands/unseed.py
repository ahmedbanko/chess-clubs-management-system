"""Unseeder which deletes everything from the database except superusers."""

from django.core.management.base import BaseCommand
from clubs.models import User, Club

class Command(BaseCommand):
        """The database unseeder."""
        def handle(self, *args, **options):
            """Removes all clubs and non superusers from the database"""
            User.objects.filter(is_staff=False, is_superuser=False).delete()
            Club.objects.all().delete()
