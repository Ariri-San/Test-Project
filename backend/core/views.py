import requests

from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action

from django.conf import settings

from djoser.views import UserViewSet as BaseUserViewSet

from . import models, serializers, permissions

# Create your views here.


class SendCodeAPIView(APIView):
    def post(self, request):
        phone_serializer = serializers.PhoneSerializer(data=request.data)
        phone_serializer.is_valid()
        
        phone = "+98" + str(phone_serializer.data["phone"])[0:]
        try:
            models.User.objects.get(phone=phone)
        except:
            return Response({"phone": ["شماره موبایل یافت نشد"]}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            "UserName": "na30makbarpour",
            "Password": "Amir110110!@#",
            "Mobile": str(phone_serializer.data["phone"]),
            "Footer": "Academy Na30m"
        }
        
        try:
            response = requests.post(url="http://smspanel.Trez.ir/AutoSendCode.ashx", data=data)
        except Exception as error:
            print("ERROR:  " + response.text)
            print(error)
            raise Response({"detail": "ارور از سمت سامانه پیامکی"}, status=status.HTTP_408_REQUEST_TIMEOUT)

        if int(response.text) >= 2000:
            return Response("کد ارسال شد", status=status.HTTP_200_OK)
        else:
            return Response({"detail": "اشکالی برای ارسال کد از سمت سامانه وجود دارد"}, status=status.HTTP_402_PAYMENT_REQUIRED)


class CheckCodeAPIView(APIView):
    def post(self, request):
        code_serializer = serializers.CheckCodeSerializer(data=request.data)
        code_serializer.is_valid()
        
        phone = "+98" + str(code_serializer.data["phone"])[0:]
        try:
            user = models.User.objects.get(phone=phone)
        except:
            return Response({"phone": ["شماره موبایل یافت نشد"]}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            "UserName": "na30makbarpour",
            "Password": "Amir110110!@#",
            "Mobile": str(code_serializer.data["phone"]),
            "Code": str(code_serializer.data["code"])
        }
        
        try:
            response = requests.post(url="http://smspanel.Trez.ir/CheckSendCode.ashx", data=data)
        except Exception as error:
            print("ERROR:  " + response.text)
            print(error)
            raise Response({"detail": "ارور از سمت سامانه پیامکی"}, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        if response.text == "true":
            user.set_password(code_serializer.data["password"])
            user.save()
            return Response("کد درست است", status=status.HTTP_200_OK)
        else:
            return Response({"code": ["کد اشتباه است"]}, status=status.HTTP_400_BAD_REQUEST)



class ConfirmCodeAPIView(APIView):
    def post(self, request):
        code_serializer = serializers.ConfirmCodeSerializer(data=request.data)
        code_serializer.is_valid()
        
        phone = "+98" + str(code_serializer.data["phone"])[0:]
        try:
            user = models.User.objects.get(phone=phone)
        except:
            return Response({"phone": ["شماره موبایل یافت نشد"]}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            "UserName": "na30makbarpour",
            "Password": "Amir110110!@#",
            "Mobile": str(code_serializer.data["phone"]),
            "Code": str(code_serializer.data["code"])
        }
        
        try:
            response = requests.post(url="http://smspanel.Trez.ir/CheckSendCode.ashx", data=data)
        except Exception as error:
            print("ERROR:  " + response.text)
            print(error)
            raise Response({"detail": "ارور از سمت سامانه پیامکی"}, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        if response.text == "true":
            user.is_active = True
            user.save()
            return Response("کد درست است", status=status.HTTP_200_OK)
        else:
            return Response({"code": ["کد اشتباه است"]}, status=status.HTTP_400_BAD_REQUEST)

