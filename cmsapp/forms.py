from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Club, ClubJoinRequest, Event, Message, EventRegistration

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    ROLES = (
        ('leader', 'Leader'),
        ('member', 'Member'),
    )
    role = forms.ChoiceField(choices=ROLES)
    phone_number = forms.CharField(max_length=15)
    
    # Leader-specific fields
    experience = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    achievements = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    certificates = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    education = forms.CharField(max_length=200, required=False)
    
    # Leader document images
    experience_image = forms.ImageField(required=False)
    achievements_image = forms.ImageField(required=False)
    certificates_image = forms.ImageField(required=False)
    education_image = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'phone_number', 'experience', 'achievements', 'certificates', 'education']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
            'role': forms.Select(attrs={'placeholder': 'Select your role'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'experience': forms.Textarea(attrs={'placeholder': 'Describe your leadership experience'}),
            'achievements': forms.Textarea(attrs={'placeholder': 'List your achievements'}),
            'certificates': forms.Textarea(attrs={'placeholder': 'List your certificates'}),
            'education': forms.TextInput(attrs={'placeholder': 'Your educational background'}),
        }

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ClubJoinRequestForm(forms.ModelForm):
    class Meta:
        model = ClubJoinRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Why do you want to join this club?'}),
        }
        
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_date', 'end_date', 'location', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        }

class EventRegistrationForm(forms.ModelForm):
    team_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    team_members = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    registration_type = forms.ChoiceField(choices=[('individual', 'Individual'), ('team', 'Team')], widget=forms.RadioSelect)

    class Meta:
        model = EventRegistration
        fields = ['registration_type', 'team_name', 'team_members']
