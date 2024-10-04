from django.urls import path
from .views import RegisterView, login_page, register_page, test_static_dir
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('api/login/', TokenObtainPairView.as_view(), name='login_api'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/', register_page, name='register'),
    path('login/', login_page, name='login'),

]
