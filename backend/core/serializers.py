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


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, min_length=11)
    
    def validate_phone(self, value):
        numbers = [str(i) for i in range(0, 10)]
        for num in value:
            if num not in numbers:
                raise serializers.ValidationError("شماره موبایل درست نیست")
        return value


class ConfirmCodeSerializer(PhoneSerializer):
    code = serializers.CharField(max_length=6, min_length=4)
    phone = serializers.CharField(max_length=11, min_length=11)
    
    def validate(self, value):
        code = value["code"]
        phone = value["phone"]

        numbers = [str(i) for i in range(0, 10)]
        for num in code:
            if num not in numbers:
                raise serializers.ValidationError("کد باید فقط عدد باشد")
        for num in phone:
            if num not in numbers:
                raise serializers.ValidationError("شماره موبایل درست نیست")
        return value



class CheckCodeSerializer(PhoneSerializer):
    code = serializers.CharField(max_length=6, min_length=4)
    phone = serializers.CharField(max_length=11, min_length=11)
    password = serializers.CharField(min_length=6, style={"input_type": "password"})
    
    def validate(self, value):
        code = value["code"]
        phone = value["phone"]
        
        numbers = [str(i) for i in range(0, 10)]
        for num in code:
            if num not in numbers:
                raise serializers.ValidationError("کد باید فقط عدد باشد")
        for num in phone:
            if num not in numbers:
                raise serializers.ValidationError("شماره موبایل درست نیست")
        return value



class DeviceUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceUser
        fields = ['id', 'name_device', 'ip_address', 'browser', 'last_seen', 'created_at']
