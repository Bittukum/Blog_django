# user/urls.py

from django.urls import path
from .views import (UserSignupView,UserLoginView,BlogPostCreateView,
                    BlogPostDetailView,BlogPostListView,CommentListCreateView,
                    LikeCreateView,SendEmailView)

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('posts/', BlogPostListView.as_view(), name='blogpost-list'),
    path('posts/create/', BlogPostCreateView.as_view(), name='blogpost-create'),
    path('posts/<int:pk>/', BlogPostDetailView.as_view(), name='blogpost-detail'),
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('like/', LikeCreateView.as_view(), name='like-create'),
    path('send-email/', SendEmailView.as_view(), name='send-email'),
]
