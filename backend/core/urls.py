from django.urls import path
from django.urls.conf import include
from core.routers import CustomRouter
from rest_framework_nested import routers
from . import views


router = CustomRouter()
# router.add_custom_root("reset_password", views.SendCodeAPIView.as_view(), "reset_password")
# router.add_custom_root("check_code", views.CheckCodeAPIView.as_view(), "check_code")
# router.add_custom_root("confirm_code", views.ConfirmCodeAPIView.as_view(), "check_code")


# URLConf
urlpatterns = router.urls
