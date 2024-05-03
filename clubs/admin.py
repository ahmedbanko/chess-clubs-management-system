from django.contrib import admin
from .models import User, Application, Membership, Club, Match

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of admin interface for users"""
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "bio",
        "experience_level",
        "is_active"
    ]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'club', 'personal_statement', 'created_at'
    ]

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'role'
    ]

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'location', 'description'
    ]

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        'player_1',
        'player_2',
        'club',
        'location',
        'date_time',
        'status',
    ]