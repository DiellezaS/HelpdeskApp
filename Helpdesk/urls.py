"""
URL configuration for Helpdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from helpdeskApp import views
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect



urlpatterns = [
    path('admin/', admin.site.urls),
    path('worker/', views.worker_dashboard, name='worker_dashboard'),
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
    path('', lambda request: redirect('login'), name='root_redirect'),

    
    path('agent/ticket/<int:ticket_id>/update/', views.update_ticket_status, name='update_ticket_status'),

    path('helpdeskApp/', include ('helpdeskApp.urls')),

    path('agent/ticket/<int:ticket_id>/claim/', views.claim_ticket, name='claim_ticket'),
    
    path('workerticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    path('agentticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail_agent'),

    # path('all-recent-events/', views.all_recent_events, name='all_recent_events'),
    path('agent/recent-events/', views.all_recent_events, name='all_recent_events'),


    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

]