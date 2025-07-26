from django.contrib import admin
from django.urls import path

from .views import (TaskViewSet, TasksAssignedToMeView, TasksReviewerView,
    BoardViewSet,
    RegistrationView, LoginView,
    EmailCheckView
)
urlpatterns = [

    #Login_Registration
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='register'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
   # Board
    path('boards/', BoardViewSet.as_view({'get': 'list', 'post': 'create'}), name='board-list'),
    path('boards/<int:pk>/', BoardViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='board-detail'),
   # Task
    path('tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('tasks/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='task-detail'),

    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', TasksReviewerView.as_view(), name='tasks-reviewer'),
]
