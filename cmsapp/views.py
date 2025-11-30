from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.db import IntegrityError
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm, ClubForm, ClubJoinRequestForm, EventForm, MessageForm
from django.contrib.auth.models import User
from .models import UserProfile, Club, Event, Message, ClubJoinRequest, ClubMembership, EventRegistration

# Club Management Views
@login_required
def club_leave_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user = request.user
    
    # Check if user is a member of the club
    membership = get_object_or_404(ClubMembership, user=user, club=club)
    
    # Check if user is the only leader
    is_only_leader = membership.is_leader and ClubMembership.objects.filter(club=club, is_leader=True).count() == 1
    
    if is_only_leader:
        messages.error(request, 'You cannot leave the club as you are the only leader. Please make someone else a leader first.')
        return redirect('club_detail', club_id=club.id)
    
    # Delete membership
    membership.delete()
    messages.success(request, f'You have left the club {club.name}.')
    return redirect('club_list')

@login_required
def club_make_leader_view(request, club_id, user_id):
    club = get_object_or_404(Club, id=club_id)
    target_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    
    # Check if current user is a leader or admin
    user_profile = UserProfile.objects.get(user=current_user)
    role = user_profile.role
    is_leader = ClubMembership.objects.filter(user=current_user, club=club, is_leader=True).exists()
    
    if not (is_leader or role == 'admin'):
        messages.error(request, 'You do not have permission to make someone a leader.')
        return redirect('club_detail', club_id=club.id)
    
    # Check if target user is a member
    try:
        membership = ClubMembership.objects.get(user=target_user, club=club)
        membership.is_leader = True
        membership.save()
        messages.success(request, f'{target_user.username} is now a leader of {club.name}.')
    except ClubMembership.DoesNotExist:
        messages.error(request, f'{target_user.username} is not a member of this club.')
    
    return redirect('club_detail', club_id=club.id)

# Messaging Views
@login_required
def message_list_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user = request.user
    
    # Check if user is a member of the club
    is_member = ClubMembership.objects.filter(user=user, club=club).exists()
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    if not (is_member or role == 'admin'):
        messages.error(request, 'You must be a member of this club to view messages.')
        return redirect('club_list')
    
    # Get all messages for this club
    club_messages = Message.objects.filter(club=club).order_by('-timestamp')
    
    # Get club members count
    members = ClubMembership.objects.filter(club=club)
    
    # Check if user is leader
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    
    # Handle new message submission
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = user
            message.club = club
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('message_list', club_id=club.id)
    else:
        form = MessageForm()
    
    context = {
        'club': club,
        'club_messages': club_messages,
        'form': form,
        'is_member': is_member,
        'role': role,
        'is_leader': is_leader,
        'members': members,
        'today': timezone.now().date(),
    }
    
    return render(request, 'cmsapp/message_list.html', context)

@login_required
def message_delete_view(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    club = message.club
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Check if user is the sender, a leader, or an admin
    is_sender = message.sender == user
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    
    if not (is_sender or is_leader or role == 'admin'):
        messages.error(request, 'You do not have permission to delete this message.')
        return redirect('message_list', club_id=club.id)
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted successfully!')
        return redirect('message_list', club_id=club.id)
    
    return render(request, 'cmsapp/message_confirm_delete.html', {'message': message, 'club': club})

# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            role = form.cleaned_data.get('role')
            
            # Get or create UserProfile (signal likely created it); then set role
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.role = role
            
            # If leader role, save additional leader information
            if role == 'leader':
                user_profile.experience = form.cleaned_data.get('experience', '')
                user_profile.achievements = form.cleaned_data.get('achievements', '')
                user_profile.certificates = form.cleaned_data.get('certificates', '')
                user_profile.education = form.cleaned_data.get('education', '')
                user_profile.phone_number = form.cleaned_data.get('phone_number', '')
                # Save uploaded images if provided
                user_profile.experience_image = form.cleaned_data.get('experience_image')
                user_profile.achievements_image = form.cleaned_data.get('achievements_image')
                user_profile.certificates_image = form.cleaned_data.get('certificates_image')
                user_profile.education_image = form.cleaned_data.get('education_image')
                user_profile.save()
            
            messages.success(request, f'Welcome {username}! Your account has been registered successfully.')
            
            # Try to log the user in automatically
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user is not None:
                login(request, user)
                # Different redirect based on role
                if role == 'leader':
                    return redirect('home')  # Leaders go to extended page
                else:
                    return redirect('home')  # Members go directly to home
            else:
                return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'cmsapp/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'cmsapp/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

# Home View
@login_required
def home_view(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    context = {
        'user_profile': user_profile,
        'role': role,
    }
    
    # Get top 5 clubs for all roles - based on members and events
    context['top_clubs_by_members'] = Club.objects.annotate(member_count=Count('clubmembership')).order_by('-member_count')[:5]
    context['top_clubs_by_events'] = Club.objects.annotate(event_count=Count('events')).order_by('-event_count')[:5]
    
    if role == 'admin':
        # Admin sees clubs they created and all events
        context['clubs'] = Club.objects.filter(created_by=user)
        # Get upcoming events
        context['events'] = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')[:5]
        # Stats for dashboard
        context['total_clubs'] = Club.objects.count()
        context['total_members'] = UserProfile.objects.filter(role='member').count()
        context['total_leaders'] = UserProfile.objects.filter(role='leader').count()
        context['total_events'] = Event.objects.count()
        context['total_messages'] = Message.objects.count()
        
        # Get clubs with most members
        context['popular_clubs'] = Club.objects.annotate(member_count=Count('clubmembership')).order_by('-member_count')[:5]
        
        # Get clubs with most events
        context['active_clubs'] = Club.objects.annotate(event_count=Count('events')).order_by('-event_count')[:5]
        
        # Get upcoming events in the next 7 days
        next_week = timezone.now() + timezone.timedelta(days=7)
        context['upcoming_week_events'] = Event.objects.filter(
            start_date__gte=timezone.now(),
            start_date__lte=next_week
        ).order_by('start_date')
        
        # Get recent messages
        context['recent_messages'] = Message.objects.order_by('-timestamp')[:10]
        
    elif role == 'leader':
        # Leader sees clubs they created and events in those clubs
        leader_clubs = Club.objects.filter(created_by=user)
        context['clubs'] = leader_clubs
        # Get upcoming events for leader's clubs
        context['events'] = Event.objects.filter(club__in=leader_clubs, start_date__gte=timezone.now()).order_by('start_date')[:5]
    else:  # member
        # Member sees clubs they joined and events in those clubs
        joined_clubs = ClubMembership.objects.filter(user=user).values_list('club', flat=True)
        context['clubs'] = Club.objects.filter(id__in=joined_clubs)
        # Get upcoming events for member's clubs
        context['events'] = Event.objects.filter(club__id__in=joined_clubs, start_date__gte=timezone.now()).order_by('start_date')[:5]
    
    return render(request, 'cmsapp/home.html', context)

@login_required
def admin_dashboard_view(request):
    # Only admins can access this view
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    if user_profile.role != 'admin':
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('home')
    
    # Basic statistics
    total_clubs = Club.objects.count()
    total_members = UserProfile.objects.filter(role='member').count()
    total_leaders = UserProfile.objects.filter(role='leader').count()
    total_events = Event.objects.count()
    total_messages = Message.objects.count()
    
    # Clubs with most members
    popular_clubs = Club.objects.annotate(member_count=Count('clubmembership')).order_by('-member_count')[:10]
    
    # Clubs with most events
    active_clubs = Club.objects.annotate(event_count=Count('events')).order_by('-event_count')[:10]
    
    # Recent join requests
    recent_join_requests = ClubJoinRequest.objects.filter(is_approved=False, is_rejected=False).order_by('-timestamp')[:15]
    
    # Pending club approvals - updated to retrieve pending clubs that need admin approval
    pending_clubs = Club.objects.filter(is_approved=False).order_by('-created_at')
    
    # Events by month (for chart)
    current_year = timezone.now().year
    events_by_month = []
    for month in range(1, 13):
        count = Event.objects.filter(
            start_date__year=current_year,
            start_date__month=month
        ).count()
        events_by_month.append(count)
    
    # User registrations by month (for chart)
    users_by_month = []
    for month in range(1, 13):
        count = User.objects.filter(
            date_joined__year=current_year,
            date_joined__month=month
        ).count()
        users_by_month.append(count)
    
    # Club status distribution for pie chart
    approved_clubs = Club.objects.filter(is_approved=True).count()
    pending_clubs_count = Club.objects.filter(is_approved=False).count()
    
    # User role distribution for pie chart
    admin_count = UserProfile.objects.filter(role='admin').count()
    leader_count = UserProfile.objects.filter(role='leader').count()
    member_count = UserProfile.objects.filter(role='member').count()
    
    # Recent activity for live monitoring (last 7 days)
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    recent_events = Event.objects.filter(start_date__gte=seven_days_ago).count()
    recent_clubs = Club.objects.filter(created_at__gte=seven_days_ago).count()
    recent_users = User.objects.filter(date_joined__gte=seven_days_ago).count()
    
    # Top 10 Leaders for promotion based on score calculation
    # Score calculation: Communication (messages sent) + Experience (account age in months) + Events organized
    current_date = timezone.now()
    leaders_with_scores = []
    
    for leader_profile in UserProfile.objects.filter(role='leader'):
        leader = leader_profile.user
        
        # Communication score: number of messages sent in last 30 days
        thirty_days_ago = current_date - timezone.timedelta(days=30)
        communication_score = Message.objects.filter(
            sender=leader,
            timestamp__gte=thirty_days_ago
        ).count()
        
        # Experience score: account age in months (max 24 months)
        account_age_days = (current_date - leader.date_joined).days
        experience_score = min(account_age_days // 30, 24)  # Cap at 24 months
        
        # Events score: number of events organized by leader's clubs
        leader_clubs = Club.objects.filter(created_by=leader)
        events_score = Event.objects.filter(club__in=leader_clubs).count()
        
        # Total score with weights: Communication 40%, Experience 30%, Events 30%
        total_score = (communication_score * 0.4) + (experience_score * 0.3) + (events_score * 0.3)
        
        # Get additional info for display
        leader_clubs_count = leader_clubs.count()
        total_members_in_clubs = ClubMembership.objects.filter(
            club__in=leader_clubs
        ).count()
        
        leaders_with_scores.append({
            'leader': leader,
            'profile': leader_profile,
            'score': round(total_score, 1),
            'communication_score': communication_score,
            'experience_score': experience_score,
            'events_score': events_score,
            'clubs_count': leader_clubs_count,
            'total_members': total_members_in_clubs,
            'account_age_months': account_age_days // 30
        })
    
    # Sort by score descending and get top 10
    top_leaders = sorted(leaders_with_scores, key=lambda x: x['score'], reverse=True)[:10]
    
    context = {
        'total_clubs': total_clubs,
        'total_members': total_members,
        'total_leaders': total_leaders,
        'total_events': total_events,
        'total_messages': total_messages,
        'popular_clubs': popular_clubs,
        'active_clubs': active_clubs,
        'recent_join_requests': recent_join_requests,
        'pending_clubs': pending_clubs,
        'events_by_month': events_by_month,
        'users_by_month': users_by_month,
        'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        # New data for pie charts
        'approved_clubs': approved_clubs,
        'pending_clubs_count': pending_clubs_count,
        'admin_count': admin_count,
        'leader_count': leader_count,
        'member_count': member_count,
        # Recent activity
        'recent_events': recent_events,
        'recent_clubs': recent_clubs,
        'recent_users': recent_users,
        # Top leaders for promotion
        'top_leaders': top_leaders,
    }
    
    return render(request, 'cmsapp/admin_dashboard.html', context)

# Profile View
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'cmsapp/profile.html', {'form': form})

# View other user's profile
@login_required
def user_profile_view(request, user_id):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Only admins can view other users' detailed profiles
    if role != 'admin':
        messages.error(request, 'You do not have permission to view other users\' profiles.')
        return redirect('home')
    
    try:
        target_user = User.objects.get(id=user_id)
        target_profile = UserProfile.objects.get(user=target_user)
        
        # Get user's clubs and leadership info
        user_clubs = Club.objects.filter(
            clubmembership__user=target_user
        ).distinct()
        
        leader_clubs = Club.objects.filter(
            clubmembership__user=target_user,
            clubmembership__is_leader=True
        ).distinct()
        
        # Get recent activity
        recent_messages = Message.objects.filter(
            sender=target_user
        ).order_by('-timestamp')[:5]
        
        context = {
            'target_user': target_user,
            'target_profile': target_profile,
            'user_clubs': user_clubs,
            'leader_clubs': leader_clubs,
            'recent_messages': recent_messages,
            'role': role,
        }
        
        return render(request, 'cmsapp/user_profile.html', context)
        
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('admin_dashboard')

# Club Views
@login_required
def club_list_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    role = user_profile.role
    
    if role == 'admin':
        # Admin sees all clubs
        clubs = Club.objects.all()
    elif role == 'leader':
        # Leader sees clubs they created and clubs they joined
        created_clubs = Club.objects.filter(created_by=request.user)
        joined_clubs = request.user.joined_clubs.all()
        clubs = (created_clubs | joined_clubs).distinct()
    else:  # member
        # Member sees clubs they joined and approved clubs they can join
        joined_clubs = request.user.joined_clubs.all()
        available_clubs = Club.objects.filter(is_approved=True).exclude(id__in=joined_clubs.values_list('id', flat=True))
        clubs = (joined_clubs | available_clubs).distinct()
    
    return render(request, 'cmsapp/club_list.html', {'clubs': clubs, 'role': role})

@login_required
def club_detail_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Check if user is a member of the club
    is_member = ClubMembership.objects.filter(user=user, club=club).exists()
    # Check if user is the leader of the club
    is_leader = is_member and ClubMembership.objects.get(user=user, club=club).is_leader
    # Check if user has a pending join request
    has_pending_request = ClubJoinRequest.objects.filter(user=user, club=club, is_approved=False, is_rejected=False).exists()
    
    # Get club events
    events = Event.objects.filter(club=club).order_by('start_date')
    
    # Get club members
    members = ClubMembership.objects.filter(club=club)
    
    # Get join requests if user is leader or admin
    join_requests = None
    if is_leader or role == 'admin':
        join_requests = ClubJoinRequest.objects.filter(club=club, is_approved=False, is_rejected=False)
    
    # Get upcoming events for this club
    events = Event.objects.filter(club=club, start_date__gte=timezone.now()).order_by('start_date')
    
    # Get club messages if user is a member
    club_messages = None
    if is_member or role == 'admin':
        club_messages = Message.objects.filter(club=club).order_by('-timestamp')
    
    context = {
        'club': club,
        'events': events,
        'members': members,
        'is_member': is_member,
        'is_leader': is_leader,
        'has_pending_request': has_pending_request,
        'join_requests': join_requests,
        'club_messages': club_messages,
        'role': role,
    }
    
    return render(request, 'cmsapp/club_detail.html', context)

@login_required
def club_create_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    role = user_profile.role
    
    # Allow both admins and leaders to create clubs
    if role != 'admin' and role != 'leader':
        messages.error(request, 'You do not have permission to create a club. Only administrators and club leaders can create clubs.')
        return redirect('club_list')
    
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES)
        if form.is_valid():
            club = form.save(commit=False)
            club.created_by = request.user
            # If admin creates, auto-approve; if leader creates, needs approval
            if role == 'admin':
                club.is_approved = True
                approval_message = f'Club "{club.name}" has been created!'
            else:  # leader
                club.is_approved = False
                approval_message = f'Club "{club.name}" has been created and is pending admin approval.'
            
            club.save()
            
            # Add creator as a member and leader
            membership = ClubMembership(user=request.user, club=club, is_leader=True)
            membership.save()
            
            messages.success(request, approval_message)
            return redirect('club_detail', club_id=club.id)
    else:
        form = ClubForm()
    
    return render(request, 'cmsapp/club_form.html', {'form': form, 'action': 'Create'})

@login_required
def club_update_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Check if user is the leader of the club or an admin
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    
    if not (is_leader or role == 'admin'):
        messages.error(request, 'You do not have permission to update this club.')
        return redirect('club_detail', club_id=club.id)
    
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            messages.success(request, f'Club "{club.name}" has been updated!')
            return redirect('club_detail', club_id=club.id)
    else:
        form = ClubForm(instance=club)
    
    return render(request, 'cmsapp/club_form.html', {'form': form, 'action': 'Update', 'club': club})

@login_required
def club_join_request_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user = request.user
    
    # Check if user is already a member
    if ClubMembership.objects.filter(user=user, club=club).exists():
        messages.info(request, 'You are already a member of this club.')
        return redirect('club_detail', club_id=club.id)
    
    # Check if user already has ANY request (pending, approved, or rejected)
    if ClubJoinRequest.objects.filter(user=user, club=club).exists():
        # If there's a pending request, just inform the user
        if ClubJoinRequest.objects.filter(user=user, club=club, is_approved=False, is_rejected=False).exists():
            messages.info(request, 'You already have a pending request to join this club.')
            return redirect('club_detail', club_id=club.id)
        else:
            # If there's a rejected request, delete it and allow a new submission
            ClubJoinRequest.objects.filter(user=user, club=club).delete()
            messages.info(request, 'Your previous request has been cleared. You can submit a new request.')
    
    if request.method == 'POST':
        form = ClubJoinRequestForm(request.POST)
        if form.is_valid():
            try:
                join_request = form.save(commit=False)
                join_request.user = user
                join_request.club = club
                join_request.save()
                messages.success(request, f'Your request to join "{club.name}" has been submitted!')
                return redirect('club_detail', club_id=club.id)
            except IntegrityError:
                # Handle case where a request already exists (race condition)
                messages.error(request, 'You already have a request for this club.')
                return redirect('club_detail', club_id=club.id)
    else:
        form = ClubJoinRequestForm()
    
    return render(request, 'cmsapp/club_join_request.html', {'form': form, 'club': club})

@login_required
def club_join_request_handle_view(request, request_id, action):
    join_request = get_object_or_404(ClubJoinRequest, id=request_id)
    club = join_request.club
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Check if user is the leader of the club or an admin
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    
    if not (is_leader or role == 'admin'):
        messages.error(request, 'You do not have permission to handle join requests.')
        return redirect('club_detail', club_id=club.id)
    
    if action == 'approve':
        # Approve the request
        join_request.is_approved = True
        join_request.save()
        
        # Add the user as a member
        membership = ClubMembership(user=join_request.user, club=club)
        membership.save()
        
        messages.success(request, f'{join_request.user.username} has been added to the club!')
    elif action == 'reject':
        # Reject the request
        join_request.is_rejected = True
        join_request.save()
        
        messages.success(request, f'Join request from {join_request.user.username} has been rejected.')
    
    return redirect('club_detail', club_id=club.id)

@login_required
def club_approval_view(request, club_id, action):
    # Only admins can approve clubs
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    if user_profile.role != 'admin':
        messages.error(request, 'You do not have permission to approve clubs.')
        return redirect('home')
    
    club = get_object_or_404(Club, id=club_id)
    
    if action == 'approve':
        # Approve the club
        club.is_approved = True
        club.save()
        messages.success(request, f'Club "{club.name}" has been approved!')
    elif action == 'reject':
        # Delete the club if rejected
        club_name = club.name
        club.delete()
        messages.success(request, f'Club "{club_name}" has been rejected and removed.')
    
    return redirect('admin_dashboard')

@login_required
def promote_to_admin_view(request, user_id):
    # Only admins can promote users to admin
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    if user_profile.role != 'admin':
        messages.error(request, 'You do not have permission to promote users to admin.')
        return redirect('home')
    
    # Get the target user
    target_user = get_object_or_404(User, id=user_id)
    target_profile = get_object_or_404(UserProfile, user=target_user)
    
    # Check if target user is currently a leader
    if target_profile.role != 'leader':
        messages.error(request, f'Only leaders can be promoted to admin. {target_user.username} is currently a {target_profile.role}.')
        return redirect('admin_dashboard')
    
    # Promote to admin
    target_profile.role = 'admin'
    target_profile.save()
    
    messages.success(request, f'{target_user.username} has been successfully promoted to admin!')
    return redirect('admin_dashboard')

@login_required
def club_leave_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user = request.user
    
    # Check if user is a member
    membership = get_object_or_404(ClubMembership, user=user, club=club)
    
    # Check if user is the only leader
    if membership.is_leader and ClubMembership.objects.filter(club=club, is_leader=True).count() == 1:
        messages.error(request, 'You cannot leave the club as you are the only leader. Transfer leadership first.')
        return redirect('club_detail', club_id=club.id)
    
    # Remove membership
    membership.delete()
    
    messages.success(request, f'You have left the club "{club.name}".')
    return redirect('club_list')

@login_required
def club_make_leader_view(request, club_id, user_id):
    club = get_object_or_404(Club, id=club_id)
    target_user = get_object_or_404(User, id=user_id)
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Check if user is the leader of the club or an admin
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    
    if not (is_leader or role == 'admin'):
        messages.error(request, 'You do not have permission to make leaders.')
        return redirect('club_detail', club_id=club.id)
    
    # Check if target user is a member
    target_membership = get_object_or_404(ClubMembership, user=target_user, club=club)
    
    # Make the target user a leader
    target_membership.is_leader = True
    target_membership.save()
    
    messages.success(request, f'{target_user.username} is now a leader of the club.')
    return redirect('club_detail', club_id=club.id)

# Event create view
@login_required
def event_create_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Check if user is the leader of the club or an admin
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    
    if not (is_leader or role == 'admin'):
        messages.error(request, 'You do not have permission to create events.')
        return redirect('club_detail', club_id=club.id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            event.created_by = user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('club_detail', club_id=club.id)
    else:
        form = EventForm()
    
    return render(request, 'cmsapp/event_form.html', {'form': form, 'club': club})

# Event update view
@login_required
def event_update_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    club = event.club
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Check if user is the leader of the club or admin
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    is_creator = event.created_by == user
    
    # Only leaders and admins can update events
    if not (is_leader or role == 'admin'):
        messages.error(request, 'You do not have permission to update this event. Only club leaders and admins can modify events.')
        return redirect('club_detail', club_id=club.id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('club_detail', club_id=club.id)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'cmsapp/event_form.html', {'form': form, 'club': club, 'event': event})

# Event delete view
@login_required
def event_delete_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    club = event.club
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Check if user is the leader of the club or admin
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    
    # Only leaders and admins can delete events
    if not (is_leader or role == 'admin'):
        messages.error(request, 'You do not have permission to delete this event. Only club leaders and admins can delete events.')
        return redirect('club_detail', club_id=club.id)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('club_detail', club_id=club.id)
    
    return render(request, 'cmsapp/event_confirm_delete.html', {'event': event})

# Event detail view
@login_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    club = event.club
    user = request.user
    
    # Check if user is a member of the club
    is_member = ClubMembership.objects.filter(user=user, club=club).exists()
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    if not (is_member or role == 'admin'):
        messages.error(request, 'You must be a member of this club to view its events.')
        return redirect('club_list')
    
    # Check if user is a leader or admin or event creator
    is_leader = ClubMembership.objects.filter(user=user, club=club, is_leader=True).exists()
    is_creator = event.created_by == user_profile
    
    # Get registered participants
    registered_participants = event.participants.all()
    
    context = {
        'event': event,
        'club': club,
        'is_leader': is_leader,
        'is_creator': is_creator,
        'role': role,
        'registered_participants': registered_participants,
    }
    
    return render(request, 'cmsapp/event_detail.html', context)

@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        # Check if the user is already registered
        if not event.participants.filter(id=request.user.id).exists():
            event.participants.add(request.user)
            messages.success(request, f'You have successfully registered for "{event.title}"!')
        else:
            messages.info(request, 'You are already registered for this event.')
    return redirect('event_detail', event_id=event.id)

# Upcoming events view
@login_required
def upcoming_events_view(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Get clubs the user is a member of
    user_clubs = ClubMembership.objects.filter(user=user).values_list('club', flat=True)
    
    # Get upcoming events from these clubs
    upcoming_events = Event.objects.filter(
        club__in=user_clubs,
        start_date__gte=timezone.now()
    ).order_by('start_date')
    
    # If user is admin, show all events
    if role == 'admin':
        upcoming_events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')
    
    context = {
        'upcoming_events': upcoming_events,
        'role': role,
    }
    
    return render(request, 'cmsapp/upcoming_events.html', context)

# Club search view
@login_required
def club_search_view(request):
    query = request.GET.get('q', '')
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    if query:
        # Search in club name and description
        if role == 'admin':
            # Admin sees all clubs matching the search
            clubs = Club.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        elif role == 'leader':
            # Leader sees clubs they created and clubs they joined matching the search
            created_clubs = Club.objects.filter(
                Q(created_by=request.user) & 
                (Q(name__icontains=query) | Q(description__icontains=query))
            )
            joined_clubs = request.user.joined_clubs.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
            clubs = (created_clubs | joined_clubs).distinct()
        else:  # member
            # Member sees clubs they joined and approved clubs they can join matching the search
            joined_clubs = request.user.joined_clubs.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
            available_clubs = Club.objects.filter(
                Q(is_approved=True) & 
                (Q(name__icontains=query) | Q(description__icontains=query))
            ).exclude(id__in=joined_clubs.values_list('id', flat=True))
            clubs = (joined_clubs | available_clubs).distinct()
    else:
        # If no query, return to club list
        return redirect('club_list')
    
    context = {
        'clubs': clubs,
        'role': role,
        'query': query,
    }
    
    return render(request, 'cmsapp/club_list.html', context)

# Event search view
@login_required
def event_search_view(request):
    query = request.GET.get('q', '')
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    if query:
        # Get clubs the user is a member of
        user_clubs = ClubMembership.objects.filter(user=user).values_list('club', flat=True)
        
        # Search in event title, description, and location
        if role == 'admin':
            # Admin sees all events matching the search
            events = Event.objects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) | 
                Q(location__icontains=query)
            ).order_by('start_date')
        else:  # leader or member
            # User sees events from their clubs matching the search
            events = Event.objects.filter(
                Q(club__in=user_clubs) & 
                (Q(title__icontains=query) | 
                Q(description__icontains=query) | 
                Q(location__icontains=query))
            ).order_by('start_date')
    else:
        # If no query, return to upcoming events
        return redirect('upcoming_events')
    
    context = {
        'upcoming_events': events,
        'role': role,
        'query': query,
    }
    
    return render(request, 'cmsapp/upcoming_events.html', context)

# Global search view
@login_required
def global_search_view(request):
    query = request.GET.get('q', '')
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    if not query:
        return redirect('home')
    
    # Get clubs the user is a member of
    user_clubs = ClubMembership.objects.filter(user=user).values_list('club', flat=True)
    
    # Search for clubs
    if role == 'admin':
        # Admin sees all clubs matching the search
        clubs = Club.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    elif role == 'leader':
        # Leader sees clubs they created and clubs they joined matching the search
        created_clubs = Club.objects.filter(
            Q(created_by=request.user) & 
            (Q(name__icontains=query) | Q(description__icontains=query))
        )
        joined_clubs = request.user.joined_clubs.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        clubs = (created_clubs | joined_clubs).distinct()
    else:  # member
        # Member sees clubs they joined and approved clubs they can join matching the search
        joined_clubs = request.user.joined_clubs.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        available_clubs = Club.objects.filter(
            Q(is_approved=True) & 
            (Q(name__icontains=query) | Q(description__icontains=query))
        ).exclude(id__in=joined_clubs.values_list('id', flat=True))
        clubs = (joined_clubs | available_clubs).distinct()
    
    # Search for events
    if role == 'admin':
        # Admin sees all events matching the search
        events = Event.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(location__icontains=query)
        ).order_by('start_date')
    else:  # leader or member
        # User sees events from their clubs matching the search
        events = Event.objects.filter(
            Q(club__in=user_clubs) & 
            (Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(location__icontains=query))
        ).order_by('start_date')
    
    # Render the global search results template with both clubs and events
    return render(request, 'cmsapp/global_search_results.html', {
        'query': query,
        'clubs': clubs,
        'events': events
    })

# Pending clubs view for admin
@login_required
def pending_clubs_view(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Only admin can view pending clubs
    if role != 'admin':
        return redirect('home')
    
    # Get all pending clubs
    pending_clubs = Club.objects.filter(is_approved=False)
    
    context = {
        'pending_clubs': pending_clubs,
        'role': role,
    }
    
    return render(request, 'cmsapp/pending_clubs.html', context)

# Leader details view
@login_required
def leader_details_view(request, user_id):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    role = user_profile.role
    
    # Get the leader's profile
    try:
        leader_user = User.objects.get(id=user_id)
        leader_profile = UserProfile.objects.get(user=leader_user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return redirect('home')
    
    # Check if the user is actually a leader (has leadership in any club)
    is_leader = ClubMembership.objects.filter(user=leader_user, is_leader=True).exists()
    if not is_leader and leader_profile.role != 'admin':
        return redirect('home')
    
    # Get clubs where this user is a leader
    leader_clubs = Club.objects.filter(
        clubmembership__user=leader_user,
        clubmembership__is_leader=True
    )
    
    context = {
        'leader_user': leader_user,
        'leader_profile': leader_profile,
        'leader_clubs': leader_clubs,
        'role': role,
    }
    
    return render(request, 'cmsapp/leader_details.html', context)

# Promote leader to admin view
@login_required
def promote_to_admin_view(request, user_id):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    
    # Only admins can promote others to admin
    if user_profile.role != 'admin':
        messages.error(request, 'You do not have permission to promote users to admin.')
        return redirect('admin_dashboard')
    
    try:
        # Get the user to be promoted
        target_user = User.objects.get(id=user_id)
        target_profile = UserProfile.objects.get(user=target_user)
        
        # Check if the target user is a leader
        if target_profile.role != 'leader':
            messages.error(request, 'Only leaders can be promoted to admin.')
            return redirect('admin_dashboard')
        
        # Promote the user to admin
        target_profile.role = 'admin'
        target_profile.save()
        
        messages.success(request, f'{target_user.username} has been successfully promoted to admin.')
        
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
    except Exception as e:
        messages.error(request, f'Error promoting user to admin: {str(e)}')
    
    return redirect('admin_dashboard')

