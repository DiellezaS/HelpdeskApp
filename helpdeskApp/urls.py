

from helpdeskApp import views as auth_views
# from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    
    path('agent/ticket/<int:ticket_id>/claim/', views.claim_ticket, name='claim_ticket'),
    
]

