import requests
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer

from rest_framework import serializers
from . import models



#  ----------  User  ----------
class UserCreateSerializer(BaseUserCreateSerializer):
    def create(self, validated_data):
        data = {
            "UserName": "na30makbarpour",
            "Password": "Amir110110!@#",
            "Mobile": "0" + str(validated_data["phone"][3:]),
            "Footer": "Academy Na30m"
        }
        
        try:
            response = requests.post(url="http://smspanel.Trez.ir/AutoSendCode.ashx", data=data)
        except Exception as error:
            print("ERROR:  " + response.text)
            print(error)
            raise serializers.ValidationError("ارور از سمت سامانه پیامکی")
        return super().create(validated_data)
    
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'phone', 'password', "username"]


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'phone', "username", 'first_name', 'last_name', 'birthday', 'skill']
