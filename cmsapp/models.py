from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    USER_ROLES = (
        ('admin', 'Admin'),
        ('leader', 'Leader'),
        ('member', 'Member'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='member')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Leader-specific fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)
    certificates = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=200, blank=True, null=True)
    
    # Leader document images
    experience_image = models.ImageField(upload_to='leader_docs/', blank=True, null=True)
    achievements_image = models.ImageField(upload_to='leader_docs/', blank=True, null=True)
    certificates_image = models.ImageField(upload_to='leader_docs/', blank=True, null=True)
    education_image = models.ImageField(upload_to='leader_docs/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_clubs')
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_clubs')
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)
    members = models.ManyToManyField(User, through='ClubMembership', related_name='joined_clubs')
    
    def __str__(self):
        return self.name

class ClubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(default=timezone.now)
    is_leader = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'club')
    
    def __str__(self):
        return f"{self.user.username} - {self.club.name}"

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    participants = models.ManyToManyField(User, related_name='participating_events', blank=True)
    
    REGISTRATION_CHOICES = [
        ('individual', 'Individual'),
        ('team', 'Team'),
    ]
    registration_type = models.CharField(
        max_length=10,
        choices=REGISTRATION_CHOICES,
        default='individual',
    )

    def __str__(self):
        return self.title
        
    @property
    def is_closed(self):
        return timezone.now() > self.end_date

class Team(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='teams')
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    members = models.ManyToManyField(User, related_name='teams')

    def __str__(self):
        return self.name

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} registered for {self.event.title}'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='club_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.club.name}"

class ClubJoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_requests')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='join_requests')
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'club')
    
    def __str__(self):
        return f"{self.user.username} - {self.club.name}"
