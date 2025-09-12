from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    RegistrationView, LoginView, EmailCheckView
)

"""
Purpose: Customizes DRF’s SimpleRouter to make the trailing slash optional.
A problem happened because DRF’s default SimpleRouter requires a trailing slash"""

class OptionalSlashRouter(SimpleRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'

router = OptionalSlashRouter()


urlpatterns = [

    # """"Login & Registration""""
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='register'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),

    path('', include(router.urls)),
]
