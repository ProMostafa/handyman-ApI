from django.test.utils import isolate_apps
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import smart_bytes, force_str, smart_str, DjangoUnicodeDecodeError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from rest_framework.decorators import api_view
from .models import User
from .utils import Util
from .serializers import UserSerializer, ChangePasswordSerializer,\
    ResetPassowrdByEmailSerializer, SetNewPasswordSeriliazer,\
    SendMessageToAdminSeriliazer, LoginSerializer, LogoutSerializer, EmailVerificationSerializer
from service.models import Order
from service.serializers import OrderSerializer
import jwt
from decouple import config
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)



    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        user.is_activated = False
        user.save()
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request)
        adsurl = f'http://localhost:3000/activate?token={str(token)}'
        ctx = {
            'user': user.username,
            'adsurl': adsurl
        }
        message = get_template('activate.html').render(ctx)
        data = {'email_body': message, 'to_email':user.email, 'email_subject': 'Verify Your Account'}
        print(data)
        Util.send_html_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)

     # disable delete method from viewset
    def destroy(self, request, *args, **kwargs):
        response = {'message': 'You Cant Delete from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

     # disable update method from viewset
    def update(self, request, *args, **kwargs):
        response = {'message': 'You Cant Update from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['GET'])
    def get_all_technical(self, request, pk=None):
        technicals = User.objects.filter(is_technical=True)
        serializer = UserSerializer(technicals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def get_technical_with_job(self, request, pk=None):
        technicals = User.objects.filter(technical_job=pk)
        print(technicals)
        print(pk)
        serializer = UserSerializer(technicals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def get_user(self, request, pk=None):
        # user = Token.objects.get(key=request.auth.key).user
        user = request.user
        user_serializer = self.serializer_class(user, many=False)
        orders = Order.objects.filter(customer=user)
        order_serializer = OrderSerializer(orders, many=True)
        response = {
            'user': user_serializer.data,
            'orders': order_serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)


class ChangeUserAvatar(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if 'avatar' in request.data:
            print(request.data['avatar'])
            # user = Token.objects.get(key=request.auth.key).user
            user = request.user
            user.avatar = request.data['avatar']
            user.save()
            serializer = UserSerializer(user, many=False)
            print(serializer.data)
            response = {
                'message': 'change avatar successfully',
                'user': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'fail': 'you need to select valid avatar'}, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmail(APIView):

    serializer_class = EmailVerificationSerializer
    token_param_config =openapi.Parameter('token',in_=openapi.IN_QUERY,description='Description', type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            data = jwt.decode(token, config('SECRET_KEY'))
            user = User.objects.get(id=data['user_id'])
            user.is_activated = True
            user.save()
            return Response({'message': 'Successfully verified Account'},status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as err:
            return Response({'error': 'Activation link Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as err:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class Refresh_token(APIView):
    def get(self, request):
        if 'email' in request.data:
            email = request.data['email']
            try:
                user = User.objects.get(email=email)
            except:
                return Response({'message': 'email must not found'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request)
            adsurl = f'http://localhost:4200/activate?token={str(token)}'
            ctx = {
                'user': user.username,
                'adsurl': adsurl
            }
            message = get_template('activate.html').render(ctx)
            data = {'email_body': message, 'to_email':user.email, 'email_subject': 'Verify Your Account'}
            print(data)
            Util.send_html_email(data)
            return Response({'message':'new message is send to activate account'}, status=status.HTTP_201_CREATED)

        return Response({'message':'email must not found'}, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'message': 'Password changed'
            }
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(APIView):
    def patch(self, request):
        serializer = SetNewPasswordSeriliazer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message':'Password reset successfully'}, status=status.HTTP_200_OK)


class RestPasswordByEmailView(APIView):
    # override post method
    def post(self, request):
        serializer = ResetPassowrdByEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data['email']
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uid64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(
                    request=request).domain
                relative_link = reverse(
                    'password_reset_confirm', kwargs={'uid64': uid64, 'token': token})
                adsurl = f'http://localhost:3000/resetpasswordconfirm?token={str(token)}&uid64={str(uid64)}'
                ctx = {
                    'user': 'customer',
                    'adsurl': adsurl
                }
                message = get_template('reset_password.html').render(ctx)
                data = {'email_body': message, 'to_email': email, 'email_subject': 'Rest your password'}
                Util.send_html_email(data)
                return Response({'success': 'We have send you a link to rest your password'}, status=status.HTTP_200_OK)
            return Response({'fail': 'This email not registrations'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordTokenCheck(APIView):
    def get(self, request, uid64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'},status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'message': 'Credentials Valid', 'uid64':uid64, 'token': token},status= status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as err:
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)


class LoginAPIView(APIView):
    print('login view')
    serializer_class = LoginSerializer

    def post(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SendMessageToAdmin(APIView):
    def post(self, request):
        serializer = SendMessageToAdminSeriliazer(data=request.data)
        if serializer.is_valid():
            message = request.data['message']
            subject = request.data['subject']
            email = request.data['email']
            data = {'email_body': message, 'to_email': email, 'email_subject': subject}
            admin = ['promostafaeladawy@gmail.com',]
            send_mail(subject=subject, message=message, from_email=email, recipient_list=admin)
            return Response({'success': True, 'message': 'Thanks for contact us '}, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors, 'message': 'Message not send '}, status=status.HTTP_400_BAD_REQUEST)
