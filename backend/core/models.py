from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.



class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    
    username = models.CharField(
        _("نام کاربری"),
        max_length=255,
        unique=True,
        help_text=_(
            "نام کاربری اجباری است و فقط می توان از اعداد حروف و @/./+/-/_ استفاده کرد"
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("این نام کاربری تکراری است"),
        },
    )
    email = models.EmailField(_("آدرس ایمیل"), unique=True)
    first_name = models.CharField(_("نام"), max_length=255, blank=True)
    last_name = models.CharField(_("نام خانوادگی"), max_length=255, blank=True)
    
    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"