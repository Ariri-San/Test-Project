from datetime import datetime, timedelta
import pytz

from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins, ViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action

from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail

from djoser.views import UserViewSet as BaseUserViewSet

from . import models, serializers, permissions

# Create your views here.




class ResetPasswordAPIView(APIView):
    serializer_class = serializers.EmailSerializer
    
    def post(self, request):
        email_serializer = serializers.EmailSerializer(data=request.data)
        email_serializer.is_valid()
        
        email = str(email_serializer.data["email"])
        user = email_serializer.get_user()
        
        try:
            old_token_user = models.TokenUser.objects.get(user_id=user.id)
            old_token_user.delete()
        except:
            pass
        
        token_user = models.TokenUser.objects.create(user_id=user.id)
        
        try:
            send_mail(
                "Subject here",
                f"The Code Is {token_user.code}",
                "shayanghodos@gmail.com",
                [email],
                fail_silently=False,
            )
            return Response("کد به ایمیل ارسال شد", status=status.HTTP_200_OK)
        except:
            return Response({"detail": "اشکالی برای ارسال کد وجود دارد"}, status=status.HTTP_402_PAYMENT_REQUIRED)


class ResetPasswordCheckAPIView(APIView):
    serializer_class = serializers.CheckCodeSerializer
    
    def post(self, request):
        code_serializer = serializers.CheckCodeSerializer(data=request.data)
        code_serializer.is_valid()
        
        code = str(code_serializer.data["code"])
        user = code_serializer.get_user()
        
        try:
            token_user = models.TokenUser.objects.get(user_id=user.id, code=code)
            now = datetime.now(pytz.timezone(settings.TIME_ZONE))
            if now > token_user.expired_datetime:
                raise
            return Response("کد درست است", status=status.HTTP_200_OK)
        except:
            return Response({"code": ["کد اشتباه است"]}, status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordConfirmAPIView(APIView):
    serializer_class = serializers.ConfirmCodeSerializer
    
    def post(self, request):
        code_serializer = serializers.ConfirmCodeSerializer(data=request.data)
        code_serializer.is_valid()
        
        code = str(code_serializer.data["code"])
        user = code_serializer.get_user()
        
        try:
            token_user = models.TokenUser.objects.get(user_id=user.id, code=code)
            now = datetime.now(pytz.timezone(settings.TIME_ZONE))
            if now > token_user.expired_datetime:
                raise
            
            user.set_password(str(code_serializer.data["password"]))
            user.save()
            return Response("پسورد عوض شد", status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except models.Token.DoesNotExist:
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

