from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import UserProfile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Check if this is the first user being created
        if User.objects.count() == 1:
            UserProfile.objects.create(user=instance, role='admin')
        else:
            UserProfile.objects.create(user=instance)
        
        # Send welcome email
        try:
            subject = render_to_string('cmsapp/emails/welcome_email_subject.txt', {'username': instance.username}).strip()
            html_message = render_to_string('cmsapp/emails/welcome_email_body.html', {
                'username': instance.username,
                'login_url': settings.LOGIN_URL, # Should ideally be absolute URI but this works for now
            })
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = instance.email

            if to_email:
                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        except Exception as e:
            # Log error or handle silently (email shouldn't block registration)
            print(f"Error sending welcome email: {e}")

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()