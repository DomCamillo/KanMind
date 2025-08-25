from django.contrib import admin
from django.urls import path, re_path,include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers
from rest_framework.routers import SimpleRouter, DefaultRouter

from .views import (TaskViewSet, TasksAssignedToMeView, TasksReviewerView,
    BoardViewSet,
    RegistrationView, LoginView, BoardUserView,
    EmailCheckView, BoardUserDetailView,CommentView, CommentDetailView
)

#Purpose: Customizes DRF’s SimpleRouter to make the trailing slash optional.
#A problem happened because DRF’s default SimpleRouter requires a trailing slash

class OptionalSlashRouter(SimpleRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'

router = OptionalSlashRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [

    # Login & Registration
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='register'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),

    # WICHTIG: Spezifische Task-URLs MÜSSEN vor den Router-URLs stehen!
    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', TasksReviewerView.as_view(), name='tasks-reviewer'),

    # Task Comments (spezifische URLs vor Router)
    path('tasks/<int:task_pk>/comments/', CommentView.as_view(), name='task-comments'),
    path('tasks/<int:task_pk>/comments/<int:pk>/', CommentDetailView.as_view(), name='task-comment-detail'),

    # BoardUser
    path('board-users/', BoardUserView.as_view(), name='boarduser-list'),
    path('board-users/<int:pk>/', BoardUserDetailView.as_view(), name='boarduser-detail'),

    path('', include(router.urls)),
]

