from random import randrange
from datetime import datetime, timedelta
import pytz

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


#  ----------  Functions  ----------
def is_number(value):
    numbers = [str(num) for num in range(10)]
    for char in value:
        if char not in numbers:
            raise ValidationError(_("%(value)s is not number"), params={"value": value})

def random_code(num):
    code = ""
    
    for _ in range(num):
        code += str(randrange(0, 9))
    
    return code
        


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



class TokenUser(models.Model):
    user = models.OneToOneField(User, verbose_name=_("کاربر"), on_delete=models.CASCADE, related_name="token")
    code = models.CharField(max_length=6, validators=[MinLengthValidator(6), is_number])
    expired_datetime = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        now = datetime.now(pytz.timezone(settings.TIME_ZONE))
        
        self.expired_datetime = now + timedelta(hours=1)
        self.code = random_code(6)
        
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.user)