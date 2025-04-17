from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views import View
from django.db import IntegrityError, transaction
from django.db.models import Q, CharField, Value, Exists, OuterRef
from itertools import chain
from django.http import HttpResponseForbidden

from .forms import (
    SignUpForm, LoginForm, UserFollowForm,
    TicketForm, ReviewForm
)
from .models import UserFollows, Ticket, Review, UserBlocks

User = get_user_model()

# Create your views here.

@login_required
def home(request):
    # Get users that the current user follows
    followed_users = User.objects.filter(
        followed_by__user=request.user
    )
    
    # Get tickets:
    # - From users you follow
    # - Your own tickets
    tickets = Ticket.objects.filter(
        Q(user=request.user) | Q(user__in=followed_users)
    ).annotate(
        content_type=Value('TICKET', CharField()),
        has_user_reviewed=Exists(
            Review.objects.filter(
                ticket=OuterRef('pk'),
                user=request.user
            )
        )
    ).select_related('user')
    
    # Get reviews:
    # - From users you follow
    # - Your own reviews
    # - Reviews on your tickets (even if reviewer is not followed)
    reviews = Review.objects.filter(
        Q(user=request.user) |  # Your reviews
        Q(user__in=followed_users) |  # Reviews from users you follow
        Q(ticket__user=request.user)  # Reviews on your tickets
    ).annotate(
        content_type=Value('REVIEW', CharField()),
    ).select_related('user', 'ticket', 'ticket__user')
    
    # Combine and sort by most recent first
    feed = sorted(
        chain(tickets, reviews),
        key=lambda x: x.time_created,
        reverse=True
    )
    
    return render(request, 'litrevu/home.html', {
        'feed': feed
    })


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('litrevu:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('litrevu:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Votre compte a été créé avec succès!')
        return response


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, 'Identifiants invalides. Veuillez réessayer.')
        return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, 'Connexion réussie!')
        return reverse_lazy('litrevu:home')


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Vous avez été déconnecté.')
            logout(request)
        return redirect('litrevu:login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Vous avez été déconnecté.')
            logout(request)
        return redirect('litrevu:login')

@login_required
def follows_list(request):
    following = request.user.following.select_related('followed_user').order_by('-time_created')
    followers = request.user.followed_by.select_related('user').order_by('-time_created')
    blocked_users = request.user.blocking.select_related('blocked_user').order_by('-time_created')
    blocked_by = request.user.blocked_by.select_related('user').order_by('-time_created')
    form = UserFollowForm(request=request)
    
    if request.method == 'POST':
        form = UserFollowForm(request.POST, request=request)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user_to_follow = User.objects.get(username=username)
                UserFollows.objects.create(
                    user=request.user,
                    followed_user=user_to_follow
                )
                messages.success(request, f"Vous suivez maintenant {username}.")
                return redirect('litrevu:follows')
            except User.DoesNotExist:
                messages.error(request, f"L'utilisateur {username} n'existe pas.")
            except IntegrityError:
                messages.error(request, "Une erreur est survenue. Veuillez réessayer.")
    
    return render(request, 'litrevu/follows.html', {
        'form': form,
        'following': following,
        'followers': followers,
        'blocked_users': blocked_users,
        'blocked_by': blocked_by
    })

@login_required
def unfollow_user(request, user_id):
    if request.method == 'POST':
        follow = get_object_or_404(
            UserFollows,
            user=request.user,
            followed_user_id=user_id
        )
        username = follow.followed_user.username
        follow.delete()
        messages.success(request, f"Vous ne suivez plus {username}.")
    return redirect('litrevu:follows')

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, 'Votre billet a été créé avec succès!')
            return redirect('litrevu:home')
    else:
        form = TicketForm()
    
    return render(request, 'litrevu/ticket_create.html', {
        'form': form
    })

@login_required
def create_review(request, ticket_id=None):
    ticket = None
    ticket_form = None
    
    if ticket_id:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        # Check if the user has already reviewed this ticket
        if Review.objects.filter(ticket=ticket, user=request.user).exists():
            messages.error(request, 'Vous avez déjà critiqué ce billet.')
            return redirect('litrevu:home')
    
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        
        if ticket_id:
            # If we're reviewing an existing ticket
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.ticket = ticket
                review.save()
                messages.success(request, 'Votre critique a été créée avec succès!')
                return redirect('litrevu:home')
        else:
            # Creating both ticket and review
            ticket_form = TicketForm(request.POST, request.FILES)
            
            if ticket_form.is_valid() and review_form.is_valid():
                try:
                    with transaction.atomic():
                        # Create ticket
                        ticket = ticket_form.save(commit=False)
                        ticket.user = request.user
                        ticket.save()
                        
                        # Create review
                        review = review_form.save(commit=False)
                        review.user = request.user
                        review.ticket = ticket
                        review.save()
                        
                        messages.success(request, 'Votre critique et le billet associé ont été créés avec succès!')
                        return redirect('litrevu:home')
                except Exception as e:
                    messages.error(request, 'Une erreur est survenue lors de la création de votre critique.')
            else:
                if not review_form.is_valid():
                    messages.error(request, 'Veuillez remplir correctement tous les champs de la critique.')
                if not ticket_form.is_valid():
                    messages.error(request, 'Veuillez remplir correctement tous les champs du billet.')
    else:
        review_form = ReviewForm()
        if not ticket_id:
            ticket_form = TicketForm()
    
    return render(request, 'litrevu/review_create.html', {
        'form': review_form,
        'ticket_form': ticket_form,
        'ticket': ticket
    })

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check if the user is the owner of the review
    if review.user != request.user:
        return HttpResponseForbidden("Vous n'avez pas la permission de modifier cette critique.")
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre critique a été modifiée avec succès!')
            return redirect('litrevu:home')
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'litrevu/review_edit.html', {
        'form': form,
        'review': review,
        'ticket': review.ticket
    })

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check if the user is the owner of the review
    if review.user != request.user:
        return HttpResponseForbidden("Vous n'avez pas la permission de supprimer cette critique.")
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Votre critique a été supprimée avec succès!')
        # Get the next parameter from the URL or default to home
        next_url = request.GET.get('next', reverse_lazy('litrevu:home'))
        return redirect(next_url)
    
    return render(request, 'litrevu/review_delete.html', {
        'review': review,
        'ticket': review.ticket,
        'next': request.GET.get('next', reverse_lazy('litrevu:home'))
    })

@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Check if the user is the owner of the ticket
    if ticket.user != request.user:
        return HttpResponseForbidden("Vous n'avez pas la permission de modifier ce billet.")
    
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre billet a été modifié avec succès!')
            return redirect('litrevu:home')
    else:
        form = TicketForm(instance=ticket)
    
    return render(request, 'litrevu/ticket_edit.html', {
        'form': form,
        'ticket': ticket
    })

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Check if the user is the owner of the ticket
    if ticket.user != request.user:
        return HttpResponseForbidden("Vous n'avez pas la permission de supprimer ce billet.")
    
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, 'Votre billet a été supprimé avec succès!')
        # Get the next parameter from the URL or default to home
        next_url = request.GET.get('next', reverse_lazy('litrevu:home'))
        return redirect(next_url)
    
    return render(request, 'litrevu/ticket_delete.html', {
        'ticket': ticket,
        'next': request.GET.get('next', reverse_lazy('litrevu:home'))
    })

@login_required
def block_user(request, user_id):
    user_to_block = get_object_or_404(User, id=user_id)
    
    # Check if trying to block self
    if user_to_block == request.user:
        messages.error(request, 'Vous ne pouvez pas vous bloquer vous-même.')
        return redirect('litrevu:follows')
    
    try:
        # Create the block
        UserBlocks.objects.create(user=request.user, blocked_user=user_to_block)
        
        # Remove any existing follow relationships in both directions
        UserFollows.objects.filter(
            Q(user=request.user, followed_user=user_to_block) |
            Q(user=user_to_block, followed_user=request.user)
        ).delete()
        
        messages.success(request, f'Vous avez bloqué {user_to_block.username}.')
    except IntegrityError:
        messages.error(request, 'Vous bloquez déjà cet utilisateur.')
    
    return redirect('litrevu:follows')

@login_required
def unblock_user(request, user_id):
    user_to_unblock = get_object_or_404(User, id=user_id)
    
    try:
        block = UserBlocks.objects.get(user=request.user, blocked_user=user_to_unblock)
        block.delete()
        messages.success(request, f'Vous avez débloqué {user_to_unblock.username}.')
    except UserBlocks.DoesNotExist:
        messages.error(request, 'Vous ne bloquez pas cet utilisateur.')
    
    return redirect('litrevu:follows')

@login_required
def posts(request):
    # Get all tickets created by the user
    tickets = Ticket.objects.filter(
        user=request.user
    ).annotate(
        content_type=Value('TICKET', CharField()),
    ).select_related('user')
    
    # Get all reviews created by the user
    reviews = Review.objects.filter(
        user=request.user
    ).annotate(
        content_type=Value('REVIEW', CharField()),
    ).select_related('user', 'ticket', 'ticket__user')
    
    # Combine and sort by most recent first
    posts = sorted(
        chain(tickets, reviews),
        key=lambda x: x.time_created,
        reverse=True
    )
    
    return render(request, 'litrevu/posts.html', {
        'posts': posts
    })
