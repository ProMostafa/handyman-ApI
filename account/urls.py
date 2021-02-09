from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import UserViewSet, UpdatePasswordView,\
    PasswordTokenCheck, RestPasswordByEmailView, VerifyEmail, SetNewPasswordView,\
    SendMessageToAdmin, Refresh_token, LoginAPIView, ChangeUserAvatar,LogoutAPIView
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = DefaultRouter()
router.register('users', UserViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('send_message/', SendMessageToAdmin.as_view(), name='send_message'),
    path('email_verify/', VerifyEmail.as_view(), name='email_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('Refresh_token/', Refresh_token.as_view(), name='Refresh_token'),
    path('change_password/', UpdatePasswordView.as_view(), name='change_password'),
    path('reset_password/', RestPasswordByEmailView.as_view(), name='reset_password'),
    path('password_reset_confirm/<uid64>/<token>/', PasswordTokenCheck.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/',SetNewPasswordView.as_view(), name='password_reset_complete'),


    path('change_avatar/', ChangeUserAvatar.as_view(), name='change_avatar')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
