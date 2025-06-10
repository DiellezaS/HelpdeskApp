
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .forms import CustomLoginForm, FAQQuestionForm, TicketForm, UpdateTicketStatusForm, CommentForm
from .models import FAQ, Ticket, Comment

from fuzzywuzzy import fuzz
from .forms import CommentForm



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
    # Get the status filter 
    status = request.GET.get('status')
    # Filter tickets 
    user_tickets = Ticket.objects.filter(created_by=request.user)
    if status:
        user_tickets = user_tickets.filter(status=status)

    ticket_form = TicketForm()
    faq_form = FAQQuestionForm()
    answer = None

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

                if best_score > 75:
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

                # Return JSON for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(response_data)

    return render(request, 'worker_dashboard.html', {
        'form': ticket_form,
        'faq_form': faq_form,
        'tickets': user_tickets,
        'answer': answer,
        'user': request.user  
    })
    
@login_required
def agent_dashboard(request):
    if request.user.role != 'agent':
        return redirect('worker_dashboard')
    
    # Get the status filter 
    status = request.GET.get('status')
    
    # Filter tickets assigned to user
    my_tickets = Ticket.objects.filter(assigned_to=request.user)
    if status:
        my_tickets = my_tickets.filter(status=status)
    
    # Get unassigned tickets (unchanged)
    unassigned_tickets = Ticket.objects.filter(status='open', assigned_to__isnull=True)
    
    return render(request, 'agent_dashboard.html', {
        'tickets': my_tickets,
        'unassigned_tickets': unassigned_tickets,
        'user': request.user
    })
    

@login_required
def claim_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, status='open', assigned_to__isnull=True)
    if request.user.role != 'agent':
        return redirect('agent_dashboard')
    
    ticket.assigned_to = request.user
    ticket.status = 'in_progress'
    ticket.save()

    return redirect('agent_dashboard')


            
@login_required
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, assigned_to=request.user)
    
    if request.method == 'POST':
        form = UpdateTicketStatusForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('agent_dashboard')
    else:
        form = UpdateTicketStatusForm(instance=ticket)

    return render(request, 'update_ticket.html', {
        'form': form,
        'ticket': ticket
    })
        


@login_required
def faq_chatbot(request):
    answer = None
    if request.method == 'POST':
        form = FAQQuestionForm(request.POST)
        if form.is_valid():
            user_question = form.cleaned_data['question']
            faqs = FAQ.objects.all()

            # Fuzzy search: krahason pyetjen e përdoruesit me ato në databazë
            best_match = None
            best_score = 0

            for faq in faqs:
                score = fuzz.partial_ratio(user_question.lower(), faq.question.lower())
                if score > best_score:
                    best_score = score
                    best_match = faq

            if best_score > 75:
                answer = best_match.answer
            else:
                Ticket.objects.create(
                    subject=f'Request from : {request.user.username}',
                    description=user_question,
                    created_by=request.user,
                    status='open'
                )
                answer = "No answer found. A ticket has been created and will be addressed by helpdesk."

    else:
        form = FAQQuestionForm()

    return render(request, 'faq_chatbot.html', {'form': form, 'answer': answer})



@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # LejoN akses nëse përdoruesi është:
    # - krijuesi i ticket-it
    # - assigned agent
    # - ose admin
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


def user_logout(request):
    logout(request)
    return redirect('login')





# import openai

# openai.api_key = "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"

# def ask_openai(prompt):
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response.choices[0].message.content.strip()
