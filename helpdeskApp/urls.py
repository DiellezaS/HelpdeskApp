

from helpdeskApp import views as auth_views
# from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('agent/ticket/<int:ticket_id>/claim/', views.claim_ticket, name='claim_ticket'),
    
    path('worker/faq-chatbot/', views.faq_chatbot, name='faq_chatbot'),
]

