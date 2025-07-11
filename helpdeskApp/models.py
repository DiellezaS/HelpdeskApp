from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth import get_user_model

from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES= (
        ('worker', 'Worker'),
        ('agent','Helpdesk Agent'),
    )
    role=models.CharField(max_length=25, choices=ROLE_CHOICES)


class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    PRIORITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )

    CATEGORY_CHOICES = (
        ('software', 'Software'),
        ('hardware', 'Hardware'),
        ('network', 'Network'),
        ('other', 'Other'),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'agent'},
        related_name='assigned_tickets'
    )
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.status}"

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question



User = get_user_model()

class Comment(models.Model):
    ticket = models.ForeignKey('Ticket', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comments from : {self.author.username} for Ticket #{self.ticket.id}'




class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        
        ('resolved', 'Resolved Ticket'),
        ('closed', 'Closed Ticket'),
        ('updated', 'Updated Ticket'),
        ('assigned', 'New Ticket Assigned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.get_type_display()} - {self.ticket.subject}"
