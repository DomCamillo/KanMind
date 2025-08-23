from django.contrib import admin
from django.urls import path, re_path,include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from .views import (TaskViewSet, TasksAssignedToMeView, TasksReviewerView,
    BoardViewSet,
    RegistrationView, LoginView, BoardUserView,
    EmailCheckView, BoardUserDetailView,CommentView, CommentDetailView
)



# router = DefaultRouter()
# router.register(r'boards', BoardViewSet, basename='board')
# router.register(r'tasks', TaskViewSet, basename='task')


# urlpatterns = [
#     # Authentication
#     path('login/', LoginView.as_view(), name='login'),
#     path('registration/', RegistrationView.as_view(), name='register'),
#     path('email-check/', EmailCheckView.as_view(), name='email-check'),

#     # Task
#     path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned'),
#     path('tasks/reviewing/', TasksReviewerView.as_view(), name='tasks-reviewer'),

#     # Comments
#     path('tasks/<int:task_pk>/comments/', CommentView.as_view(), name='task-comments'),
#     path('tasks/<int:task_pk>/comments/<int:pk>/', CommentDetailView.as_view(), name='task-comment-detail'),

#     # BoardUser
#     path('board-users/', BoardUserView.as_view(), name='boarduser-list'),
#     path('board-users/<int:pk>/', BoardUserDetailView.as_view(), name='boarduser-detail'),

#     path('', include(router.urls)),
# ]






urlpatterns = [

    #Login_Registration
    path('login/',LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='register'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
   # Board
    path('boards/', BoardViewSet.as_view({'get': 'list', 'post': 'create'}), name='board-list'),
    re_path(r'^boards/(?P<pk>\d+)/?$', BoardViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='board-detail'),
   # Task
    path('tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('tasks/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'put': 'update','patch': 'partial_update', 'delete': 'destroy'}), name='task-detail'),

    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', TasksReviewerView.as_view(), name='tasks-reviewer'),

    path('tasks/<int:task_pk>/comments/', CommentView.as_view(), name='task-comments'),
    path('tasks/<int:task_pk>/comments/<int:pk>/', CommentDetailView.as_view(), name='task-comment-detail'),

    # Column
    #path('columns/', ColumnView.as_view(), name='column-list'),
    #path('columns/<int:pk>/', ColumnDetailView.as_view(), name='column-detail'),

    # BoardUser
    path('board-users/', BoardUserView.as_view(), name='boarduser-list'),
    path('board-users/<int:pk>/', BoardUserDetailView.as_view(), name='boarduser-detail'),
]
