from django.contrib import admin
from .models import UserProfile, Club, ClubMembership, Event, Message, ClubJoinRequest

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'date_joined')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('name', 'description')

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'date_joined', 'is_leader')
    list_filter = ('is_leader',)
    search_fields = ('user__username', 'club__name')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'created_by', 'start_date', 'end_date')
    list_filter = ('club',)
    search_fields = ('title', 'description', 'location')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'club', 'timestamp', 'is_read')
    list_filter = ('is_read', 'club')
    search_fields = ('content', 'sender__username')

@admin.register(ClubJoinRequest)
class ClubJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'timestamp', 'is_approved', 'is_rejected')
    list_filter = ('is_approved', 'is_rejected')
    search_fields = ('user__username', 'club__name')
