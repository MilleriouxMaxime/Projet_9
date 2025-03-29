from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'litrevu'

urlpatterns = [
    # Authentication
    path('', RedirectView.as_view(pattern_name='litrevu:login'), name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Main pages
    path('home/', views.home, name='home'),
    path('posts/', views.posts, name='posts'),
    
    # Following
    path('follows/', views.follows_list, name='follows'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow'),

    # Tickets and Reviews
    path('ticket/create/', views.create_ticket, name='create_ticket'),
    path('ticket/edit/<int:ticket_id>/', views.edit_ticket, name='edit_ticket'),
    path('ticket/delete/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('review/create/', views.create_review, name='create_review'),
    path('review/create/<int:ticket_id>/', views.create_review, name='create_review_for_ticket'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
] 