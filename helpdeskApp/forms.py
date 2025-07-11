
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Ticket, Comment


class CustomLoginForm(AuthenticationForm):
    
    
    ROLE_CHOICES= (
        ('worker', 'Worker'),
        ('agent','Helpdesk Agent'),
    
    ) 
    
    username=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'description', 'priority', 'category']
        widgets = {
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

# class UpdateTicketStatusForm(forms.ModelForm):
#     class Meta:
#         model = Ticket
#         fields = ['status']
        
class UpdateTicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'priority']
        widgets = {
            'status': forms.Select(choices=Ticket.STATUS_CHOICES),
            'priority': forms.Select(choices=Ticket.PRIORITY_CHOICES),
        }
    
class FAQQuestionForm(forms.Form):
    question = forms.CharField(label='your question', max_length=255)
    
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }