from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import UserRegistration
# Register your models here.

@admin.register(UserRegistration)
class UserRegistrationAdmin(UserAdmin):
    list_display = ['email', 'username', 'phone', 'registration_to_school', 'campus', 'dormitoryA', 'dormitoryB']
    fieldsets = list(UserAdmin.fieldsets)
    fieldsets[1] = (_('Personal info'), {'fields': ('email', 'phone', 'registration_to_school', 'campus', 'dormitoryA', 'dormitoryB', 'repairEmployee')})


# 注册模型，让其能显示在django自带的admin管理界面中
# admin.site.register(UserRegistration, UserAdmin)



