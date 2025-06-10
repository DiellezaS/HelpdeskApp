
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

    role = forms.ChoiceField(
        choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'})
    )


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'description']





class UpdateTicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']
        
        
    
class FAQQuestionForm(forms.Form):
    question = forms.CharField(label='your question', max_length=255)
    
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }