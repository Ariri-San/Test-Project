import requests
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer

from rest_framework import serializers
from . import models



#  ----------  User  ----------
class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']



#  ----------  User Code  ----------
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def get_user(self, validate_data=None):
        if validate_data == None:
            validate_data = self.data
        
        email = str(validate_data["email"])
        
        try:
            user = models.User.objects.get(email=email)
            return user
        except:
            raise serializers.ValidationError("کاربری با این ایمیل پیدا نشد")


class CheckCodeSerializer(EmailSerializer):
    code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_code(self, value):
        numbers = [str(i) for i in range(0, 10)]
        for num in value:
            if num not in numbers:
                raise serializers.ValidationError("کد باید فقط عدد باشد")
        return value


class ConfirmResetPasswordSerializer(CheckCodeSerializer):
    password = serializers.CharField(style={"input_type": "password"})
    
    def validate_password(self, value):
        user = self.get_user(self.validated_data)
        validate_password(value, user)
        return value


class ConfirmResetUsernameSerializer(CheckCodeSerializer):
    username = serializers.CharField(validators=[UnicodeUsernameValidator])
    
    def validate_username(self, value):
        if models.User.objects.filter(username=value).exists():
            raise serializers.ValidationError("نام کاربری تکراری است")
        return value

