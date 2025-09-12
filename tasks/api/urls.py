from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    TaskViewSet, TasksAssignedToMeView, TasksReviewerView,
    CommentView, CommentDetailView
)
"""
Purpose: Customizes DRF’s SimpleRouter to make the trailing slash optional.
A problem happened because DRF’s default SimpleRouter requires a trailing slash"""
class OptionalSlashRouter(SimpleRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'

router = OptionalSlashRouter()

router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [

    #"""Tasks"""
    path('tasks/assigned-to-me/', TasksAssignedToMeView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', TasksReviewerView.as_view(), name='tasks-reviewer'),

    # """ Task Comments"""
    path('tasks/<int:task_pk>/comments/', CommentView.as_view(), name='task-comments'),
    path('tasks/<int:task_pk>/comments/<int:pk>/', CommentDetailView.as_view(), name='task-comment-detail'),


    path('', include(router.urls)),
]
