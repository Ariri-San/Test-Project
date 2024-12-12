from datetime import datetime, timedelta
import pytz

from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins, ViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail

from djoser.views import get_user_email, signals
from django.contrib.auth.tokens import default_token_generator
from djoser.conf import settings as settings_djoser

from . import models, serializers, permissions

# Create your views here.


class UserViewSet(ModelViewSet):
    serializer_class = settings_djoser.SERIALIZERS.user
    queryset = models.User.objects.all()
    permission_classes = settings_djoser.PERMISSIONS.user
    token_generator = default_token_generator
    lookup_field = settings_djoser.USER_ID_FIELD

    def permission_denied(self, request, **kwargs):
        if (
            settings_djoser.HIDE_USERS
            and request.user.is_authenticated
            and self.action in ["update", "partial_update", "list", "retrieve"]
        ):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings_djoser.HIDE_USERS and self.action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset
    
    def get_instance(self):
        return self.request.user

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {"user": user}
        to = [get_user_email(user)]
        if settings_djoser.SEND_ACTIVATION_EMAIL:
            settings_djoser.EMAIL.activation(self.request, context).send(to)
        elif settings_djoser.SEND_CONFIRMATION_EMAIL:
            settings_djoser.EMAIL.confirmation(self.request, context).send(to)

    def perform_update(self, serializer, *args, **kwargs):
        super().perform_update(serializer, *args, **kwargs)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

        # should we send activation email after update?
        if settings_djoser.SEND_ACTIVATION_EMAIL and not user.is_active:
            context = {"user": user}
            to = [get_user_email(user)]
            settings_djoser.EMAIL.activation(self.request, context).send(to)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    
    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings_djoser.PERMISSIONS.user_create
        elif self.action == "list":
            self.permission_classes = settings_djoser.PERMISSIONS.user_list
        elif self.action == "destroy" or (
            self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            self.permission_classes = settings_djoser.PERMISSIONS.user_delete
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            if settings_djoser.USER_CREATE_PASSWORD_RETYPE:
                return settings_djoser.SERIALIZERS.user_create_password_retype
            return settings_djoser.SERIALIZERS.user_create
        elif self.action == "destroy" or (
            self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            return settings_djoser.SERIALIZERS.user_delete
        elif self.action == "me":
            return settings_djoser.SERIALIZERS.current_user

        return self.serializer_class

    @action(["get", "put", "patch", "delete"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)



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
                return Response({"detail": ["کد باطل شده است لطفا دوباره کد را ارسال کنید"]}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"detail": ["کد باطل شده است لطفا دوباره کد را ارسال کنید"]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(str(code_serializer.data["password"]))
            user.save()
            return Response("پسورد عوض شد", status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except models.Token.DoesNotExist:
            return Response({"detail": ["کد اشتباه است"]}, status=status.HTTP_400_BAD_REQUEST)

