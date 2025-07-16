from datetime import timedelta, timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .forms import CustomLoginForm, FAQQuestionForm, TicketForm, UpdateTicketStatusForm, CommentForm
from .models import FAQ, ActivityLog, Ticket, Comment
from fuzzywuzzy import fuzz
from .forms import CommentForm
from django.db.models import Q
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils.timezone import now, timedelta
from django.utils.dateparse import parse_date
from datetime import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta
from django.utils import timezone
from .forms import CommentForm
from .models import Comment, Ticket
from django.http import JsonResponse
from itertools import chain

def user_login(request):
    if request.user.is_authenticated:
        return redirect('worker_dashboard' if request.user.role == 'worker' else 'agent_dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('worker_dashboard' if user.role == 'worker' else 'agent_dashboard')
            
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})
    
    
@login_required
def worker_dashboard(request):
    if request.user.role != 'worker':
        return redirect('agent_dashboard')

    faqs = FAQ.objects.all()
    show_all = request.GET.get('show_all') == '1'
    status = request.GET.get('status')
    category = request.GET.get('category')
    priority = request.GET.get('priority')
    search_query = request.GET.get('search', '').strip()
    created_from_str = request.GET.get('created_from')
    created_to_str = request.GET.get('created_to')

    user_tickets = Ticket.objects.filter(created_by=request.user)

    if not show_all:
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        user_tickets = user_tickets.filter(created_at__gte=seven_days_ago)

    if status:
        user_tickets = user_tickets.filter(status=status)

    if category:
        user_tickets = user_tickets.filter(category=category)

    if priority:
        user_tickets = user_tickets.filter(priority=priority)

    created_from = None
    created_to = None

    if created_from_str:
        try:
            created_from = datetime.strptime(created_from_str, "%Y-%m-%d")
            user_tickets = user_tickets.filter(created_at__gte=created_from)
        except ValueError:
            pass

    if created_to_str:
        try:
            created_to = datetime.strptime(created_to_str, "%Y-%m-%d") + timedelta(days=1)
            user_tickets = user_tickets.filter(created_at__lt=created_to)
        except ValueError:
            pass

    if search_query:
        user_tickets = user_tickets.filter(
            Q(subject__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(id__iexact=search_query)
        )

    # Trend chart data
    ticket_trends = (
        Ticket.objects
        .filter(created_by=request.user)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    trend_dates_raw = [entry['date'].strftime('%Y-%m-%d') for entry in ticket_trends]
    trend_labels = [entry['date'].strftime('%b %d') for entry in ticket_trends]
    trend_counts = [entry['count'] for entry in ticket_trends]

    # Ticket status counts
    all_tickets = Ticket.objects.filter(created_by=request.user)
    open_count = all_tickets.filter(status='open').count()
    in_progress_count = all_tickets.filter(status='in_progress').count()
    resolved_count = all_tickets.filter(status='resolved').count()
    closed_count = all_tickets.filter(status='closed').count()

    accepted_tickets = all_tickets.filter(status='in_progress', assigned_to__isnull=False)

    # Category chart
    category_stats = all_tickets.values('category').annotate(count=Count('id'))
    category_labels = [item['category'].capitalize() for item in category_stats]
    category_counts = [item['count'] for item in category_stats]
    

    recent_comments = Comment.objects.filter(ticket__created_by=request.user).select_related('ticket', 'author').order_by('-created_at')[:10]
    recent_activity = ActivityLog.objects.filter(ticket__created_by=request.user).select_related('ticket', 'user').order_by('-timestamp')[:10]


    for comment in recent_comments:
        comment.event_type = 'comment'
        comment.event_time = comment.created_at

    for activity in recent_activity:
        activity.event_type = 'activity'
        activity.event_time = activity.timestamp

    # Bashkoj activitys me komentet
    recent_events = sorted(
        chain(recent_comments, recent_activity),
        key=lambda x: x.event_time,
        reverse=True
    )[:5]

    # Forms
    ticket_form = TicketForm()
    faq_form = FAQQuestionForm()
    answer = None

    # Handle POST
    if request.method == 'POST':
        if 'submit_ticket' in request.POST:
            ticket_form = TicketForm(request.POST)
            if ticket_form.is_valid():
                ticket = ticket_form.save(commit=False)
                ticket.created_by = request.user
                ticket.save()
                return redirect('worker_dashboard')

        elif 'submit_question' in request.POST:
            faq_form = FAQQuestionForm(request.POST)
            if faq_form.is_valid():
                user_question = faq_form.cleaned_data['question']
                best_match = None
                best_score = 0

                for faq in faqs:
                    score = fuzz.partial_ratio(user_question.lower(), faq.question.lower())
                    if score > best_score:
                        best_score = score
                        best_match = faq

                if best_score > 65:
                    answer = best_match.answer
                    response_data = {"status": "answered", "answer": answer}
                else:
                    ticket = Ticket.objects.create(
                        subject=f'Request from: {request.user.username}',
                        description=user_question,
                        created_by=request.user,
                        status='open'
                    )
                    answer = "No answer found. A ticket has been created and will be addressed by helpdesk."
                    response_data = {"status": "ticket_created", "ticket_id": ticket.id}

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(response_data)

    return render(request, 'worker_dashboard.html', {
        'form': ticket_form,
        'faq_form': faq_form,
        'tickets': user_tickets,
        'answer': answer,
        'user': request.user,
        'status': status,
        'category': category,
        'priority': priority,
        'open_count': open_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'recent_comments': recent_comments,
        'search_query': search_query,
        'trend_labels': json.dumps(trend_labels),
        'trend_dates_raw': json.dumps(trend_dates_raw),
        'trend_counts': json.dumps(trend_counts),
        'category_labels': json.dumps(category_labels),
        'category_counts': json.dumps(category_counts),
        'accepted_tickets': accepted_tickets,
        'created_from': created_from,
        'created_to': created_to,
        'show_all': show_all,
        'recent_events': recent_events,
    })
    

@login_required
def agent_dashboard(request):
    if request.user.role != 'agent':
        return redirect('worker_dashboard')

    status = request.GET.get('status')
    category = request.GET.get('category')
    priority = request.GET.get('priority')
    created_from = request.GET.get('created_from')
    created_to = request.GET.get('created_to')
    search_query = request.GET.get('search', '').strip()
    
        # show_all=1 show all tickets, else last 7 days
    show_all = request.GET.get('show_all') == '1'


    my_tickets = Ticket.objects.filter(assigned_to=request.user)
    
     # Filter for last 7 days unless show_all 
    if not show_all:
        seven_days_ago = timezone.now() - timedelta(days=7)

        my_tickets = my_tickets.filter(created_at__gte=seven_days_ago)


    #  status category priority filters
    if status:
        my_tickets = my_tickets.filter(status=status)

    if category:
        my_tickets = my_tickets.filter(category=category)

    if priority:
        my_tickets = my_tickets.filter(priority=priority)

    # date range filters
    created_from_str = request.GET.get('created_from')
    created_to_str = request.GET.get('created_to')

    if created_from_str:
        try:
            created_from = datetime.strptime(created_from_str, "%Y-%m-%d")
            my_tickets = my_tickets.filter(created_at__gte=created_from)
        except ValueError:
            pass

    if created_to_str:
        try:
            created_to = datetime.strptime(created_to_str, "%Y-%m-%d") + timedelta(days=1)
            my_tickets = my_tickets.filter(created_at__lt=created_to)
        except ValueError:
            pass

    #  search filter
    if search_query:
        my_tickets = my_tickets.filter(
            Q(subject__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(id__iexact=search_query)
        )
    
    all_agent_tickets = Ticket.objects.filter(assigned_to=request.user)
    
    open_count = all_agent_tickets.filter(status='open').count()
    in_progress_count = all_agent_tickets.filter(status='in_progress').count()
    resolved_count = all_agent_tickets.filter(status='resolved').count()
    closed_count = all_agent_tickets.filter(status='closed').count()

    ticket_stats = all_agent_tickets.values('status').annotate(count=Count('id'))
    priority_stats = all_agent_tickets.values('priority').annotate(count=Count('id'))

    tickets_over_time = (
        all_agent_tickets
        .filter(created_at__gte=timezone.now() - timedelta(days=30))
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
        
    unassigned_tickets = Ticket.objects.filter(status='open', assigned_to__isnull=True)
    
    recent_comments = Comment.objects.filter(ticket__assigned_to=request.user).select_related('ticket', 'author').order_by('-created_at')[:10]
    recent_activity = ActivityLog.objects.filter(user=request.user).select_related('ticket', 'user').order_by('-timestamp')[:10]

    for comment in recent_comments:
        comment.event_type = 'comment'
        comment.event_time = comment.created_at

    for activity in recent_activity:
        activity.event_type = 'activity'
        activity.event_time = activity.timestamp

    recent_events = sorted(
        chain(recent_comments, recent_activity),
        key=lambda x: x.event_time,
        reverse=True
    )[:5]

    
    if request.user.is_staff:
        User = get_user_model()
        agent_stats = Ticket.objects.filter(assigned_to__isnull=False).values('assigned_to__username').annotate(count=Count('id'))

        agent_labels = [item['assigned_to__username'] for item in agent_stats]
        agent_counts = [item['count'] for item in agent_stats]
    else:
        agent_labels = []
        agent_counts = []
            
    priority_counts = {item['priority']: item['count'] for item in priority_stats}
    high_count = priority_counts.get('high', 0)
    medium_count = priority_counts.get('medium', 0)
    low_count = priority_counts.get('low', 0)

   

    return render(request, 'agent_dashboard.html', {
        'my_ticket': my_tickets,
        'tickets': my_tickets,
        'unassigned_tickets': unassigned_tickets,
        'user': request.user,
        'open_count': open_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'recent_comments': recent_comments,
        'search_query': search_query,
        'priority': priority,
        'status': status,
        'category': category,
        'created_from': created_from,
        'created_to': created_to,
        'ticket_stats': list(ticket_stats),
        'priority_stats': list(priority_stats),
        'tickets_over_time': json.dumps(list(tickets_over_time), cls=DjangoJSONEncoder), 
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count,
        'agent_labels': json.dumps(agent_labels),
        'agent_counts': json.dumps(agent_counts),
        'show_all': show_all, 
        'recent_activity': recent_activity,
        'recent_events': recent_events,
    })
    
@login_required
def all_recent_events(request):
    if request.user.role != 'agent':
        return redirect('worker_dashboard')

    recent_comments = Comment.objects.filter(ticket__assigned_to=request.user).select_related('ticket', 'author')
    recent_activity = ActivityLog.objects.filter(user=request.user).select_related('ticket', 'user')

    for comment in recent_comments:
        comment.event_type = 'comment'
        comment.event_time = comment.created_at

    for activity in recent_activity:
        activity.event_type = 'activity'
        activity.event_time = activity.timestamp

    all_events = sorted(
        chain(recent_comments, recent_activity),
        key=lambda x: x.event_time,
        reverse=True
    )

    return render(request, 'partials/recent_events_list.html', {
        'recent_events': all_events,
    })



@login_required
def claim_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, status='open', assigned_to__isnull=True)
    
    if request.user.role != 'agent':
        return redirect('agent_dashboard')
    
    ticket.assigned_to = request.user
    ticket.status = 'in_progress'
    ticket.save()

    #Regjistro aktivitetin
    ActivityLog.objects.create(
        user=request.user,
        ticket=ticket,
        type='assigned'
    )

    return redirect('agent_dashboard')

@login_required
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, assigned_to=request.user)
    form = UpdateTicketStatusForm(request.POST or None, instance=ticket)

    if request.method == 'POST' and form.is_valid():
        previous_status = ticket.status  
        updated_ticket = form.save()

        # Cakton llojin e aktivitetit në bazë të statusit të ri
        new_status = updated_ticket.status
        if new_status == 'resolved':
            activity_type = 'resolved'
        elif new_status == 'closed':
            activity_type = 'closed'
        elif new_status != previous_status:
            activity_type = 'updated'
        else:
            activity_type = None  # nuk ka ndryshim

        # Ruan  nëse ka ndodhur ndryshim
        if activity_type:
            ActivityLog.objects.create(
                user=request.user,
                ticket=updated_ticket,
                type=activity_type
            )

        return redirect('agent_dashboard')

    return render(request, 'update_ticket.html', {
        'ticket': ticket,
        'form': form,
    })
        
@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Check permissions
    if request.user != ticket.created_by and request.user != ticket.assigned_to and not request.user.is_staff:
        return HttpResponseForbidden()

    comments = ticket.comments.all().order_by('created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
    
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = CommentForm()
    
    return render(request, 'ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'form': form,
    })
    
    
@login_required
def ticket_detail_modal(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.user != ticket.created_by and request.user != ticket.assigned_to and not request.user.is_staff:
        return HttpResponseForbidden()

    comments = ticket.comments.all().order_by('created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()

            comments = ticket.comments.all().order_by('created_at')
            form = CommentForm()
    else:
        form = CommentForm()

    return render(request, 'ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'form': form,
    })


def user_logout(request):
    logout(request)
    return redirect('login')
