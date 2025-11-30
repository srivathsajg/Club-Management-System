from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Home and Profile URLs
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Club URLs
    path('clubs/', views.club_list_view, name='club_list'),
    path('clubs/create/', views.club_create_view, name='club_create'),
    path('clubs/<int:club_id>/', views.club_detail_view, name='club_detail'),
    path('clubs/<int:club_id>/update/', views.club_update_view, name='club_update'),
    path('clubs/<int:club_id>/join/', views.club_join_request_view, name='club_join_request'),
    path('clubs/join-request/<int:request_id>/<str:action>/', views.club_join_request_handle_view, name='club_join_request_handle'),
    path('clubs/<int:club_id>/leave/', views.club_leave_view, name='club_leave'),
    path('clubs/<int:club_id>/make-leader/<int:user_id>/', views.club_make_leader_view, name='club_make_leader'),
    path('leader/<int:user_id>/details/', views.leader_details_view, name='leader_details'),
    path('user/<int:user_id>/profile/', views.user_profile_view, name='user_profile'),
    path('promote-to-admin/<int:user_id>/', views.promote_to_admin_view, name='promote_to_admin'),
    path('clubs/<int:club_id>/approval/<str:action>/', views.club_approval_view, name='club_approval'),
    path('clubs/search/', views.club_search_view, name='club_search'),
    path('pending-clubs/', views.pending_clubs_view, name='pending_clubs'),
    path('club-approval/<int:club_id>/<str:action>/', views.club_approval_view, name='club_approval'),
    # Global search
    path('search/', views.global_search_view, name='global_search'),
    
    # Event URLs
    path('clubs/<int:club_id>/events/create/', views.event_create_view, name='event_create'),
    path('events/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('events/<int:event_id>/update/', views.event_update_view, name='event_update'),
    path('events/<int:event_id>/delete/', views.event_delete_view, name='event_delete'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('events/upcoming/', views.upcoming_events_view, name='upcoming_events'),
    path('events/search/', views.event_search_view, name='event_search'),
    
    # Message URLs
    path('clubs/<int:club_id>/messages/', views.message_list_view, name='message_list'),
    path('messages/<int:message_id>/delete/', views.message_delete_view, name='message_delete'),
]