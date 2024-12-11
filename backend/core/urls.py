from django.urls import path
from django.urls.conf import include
from core.routers import CustomRouter
from rest_framework_nested import routers
from . import views


router = CustomRouter()
router.add_custom_root("reset_password", views.ResetPasswordAPIView.as_view(), "reset_password")
router.add_custom_root("check_code", views.ResetPasswordCheckAPIView.as_view(), "check_code")
router.add_custom_root("confirm_code", views.ResetPasswordConfirmAPIView.as_view(), "confirm_code")


# URLConf
urlpatterns = router.urls
