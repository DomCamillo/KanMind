from django.contrib import admin
from django.urls import path ,include
from .views import  BoardUserView, BoardUserDetailView ,TaskView ,TaskDetailView, BaordView, BoardDetailView, ColumnView, ColumnDetailView,CommentView, CommentDetailView

urlpatterns = [

   path('tasks/', TaskView.as_view(), name='Task-list'),
   path('tasks/<int:pk>', TaskDetailView.as_view(), name='TaskDetail-list'),
   path('board/', BaordView.as_view(), name='Board-list'),
   path('board/<int:pk>', BoardDetailView.as_view(), name='BoardDetail-list'),
   path('user/', BoardUserView.as_view(), name='User-list'),
   path('user/<int:pk>', BoardUserDetailView.as_view(), name='UserDetail-list'),
   path('comment/', CommentView.as_view(), name='Comment-list'),
   path('comment/<int:pk>', CommentDetailView.as_view(), name='CommentDetail-list'),
   path('column/', ColumnView.as_view(), name='Column-list'),
   path('column/<int:pk>', ColumnDetailView.as_view(), name='ColumnDetail-list'),

]
