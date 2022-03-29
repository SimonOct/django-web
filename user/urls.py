from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # 注册相关
    path('signup/', views.registration, name='registration'),
    path('isduplicate', views.checkDuplicate, name='isduplicate'),
    path('emailvalidation', views.emailValidation, name='emailvalidation'),
    # 登录相关
    path('signin/', views.login, name='login'),
    # 注销相关
    path('logout/', views.logout, name='logout'),
    # 忘记密码
    path('forgot/', views.forgot, name='forgot'),
    # 重置密码
    path('reset', views.reset, name='reset'),
    # 用户个人信息
    path('myinfo/', views.user_info, name='user_info'),
    # 修改用户个人信息
    # 修改邮箱.
    path('changeInfo/', views.change_user_info, name='changeInfo'),
    path('changeInfo/emailcode', views.email_change_code, name='emailChangeCode')
]
