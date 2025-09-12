from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    BoardViewSet, BoardUserView, BoardUserDetailView
)

"""
Purpose: Customizes DRF’s SimpleRouter to make the trailing slash optional.
A problem happened because DRF’s default SimpleRouter requires a trailing slash"""

class OptionalSlashRouter(SimpleRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'

router = OptionalSlashRouter()
router.register(r'boards', BoardViewSet, basename='board')


urlpatterns = [


    # """BoardUser"""
    path('board-users/', BoardUserView.as_view(), name='boarduser-list'),
    path('board-users/<int:pk>/', BoardUserDetailView.as_view(), name='boarduser-detail'),

    path('', include(router.urls)),
]