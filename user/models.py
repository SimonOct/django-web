from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.
    
class UserRegistration(AbstractUser):

    email = models.EmailField(verbose_name='邮箱', max_length=255, null=False, unique=True)
    email_is_verified = models.BooleanField(verbose_name='是否验证成功', default=False)
    username = models.CharField(verbose_name='用户名', max_length=15, null=False, unique=True)
    password = models.CharField(verbose_name='密码', max_length=128, null=False)
    registration_to_school = models.IntegerField(verbose_name='入学年份', null=False, default=0000)
    campus = models.CharField(verbose_name='校区', max_length=15, null=False, default='None')
    dormitoryA = models.CharField(verbose_name='宿舍楼', max_length=15, null=False, default='NA')
    dormitoryB = models.IntegerField(verbose_name='宿舍号', null=False, default=0000)
    phone = models.IntegerField(verbose_name='手机号码', default=0000)
    sex = models.CharField(verbose_name='性别', max_length=15, null=False, default='NA')
    birthday = models.CharField(verbose_name='生日', max_length=15, default='NA')
    repairEmployee = models.BooleanField(verbose_name='是否为维修员', default=False)
    info_updated_time = models.DateTimeField(
        verbose_name='用户信息更新时间', auto_now=True)

class EmailValidation(models.Model):

    email = models.CharField(verbose_name='邮箱', max_length=30, null=False)
    email_code = models.CharField(verbose_name='uuid', max_length=36, unique=True)
    create_time = models.DateTimeField(verbose_name='生成时间', auto_now_add=True)

class EmailCheck(models.Model):

    email = models.CharField(verbose_name='邮箱', max_length=30, null=False)
    email_code = models.CharField(verbose_name='uuid', max_length=36, unique=True)
    create_time = models.DateTimeField(verbose_name='生成时间', auto_now_add=True)

class EmailChange(models.Model):

    user_id = models.BigIntegerField(verbose_name='用户id', default=0)
    email = models.EmailField(verbose_name='邮箱')
    email_code = models.CharField(verbose_name='代码', max_length=8, unique=True)
    create_time = models.DateTimeField(verbose_name='生成时间', auto_now_add=True)
