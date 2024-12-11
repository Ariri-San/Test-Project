import requests
from django.contrib.auth.password_validation import validate_password
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
    
    def validate(self, validate_data):
        code = validate_data["code"]
        
        numbers = [str(i) for i in range(0, 10)]
        for num in code:
            if num not in numbers:
                raise serializers.ValidationError("کد باید فقط عدد باشد")
        
        return validate_data



class ConfirmCodeSerializer(EmailSerializer):
    code = serializers.CharField(max_length=6, min_length=6)
    password = serializers.CharField(style={"input_type": "password"})
    
    def validate(self, validate_data):
        user = self.get_user(validate_data)
        
        validate_password(validate_data["password"], user)

        code = validate_data["code"]
        
        numbers = [str(i) for i in range(0, 10)]
        for num in code:
            if num not in numbers:
                raise serializers.ValidationError("کد باید فقط عدد باشد")
        return validate_data

