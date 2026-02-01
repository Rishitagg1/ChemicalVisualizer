from django.urls import path
from .views import UploadView, SignupView, LoginView, UpdateProfileView

urlpatterns = [
    path('upload/', UploadView.as_view(), name='upload'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
]