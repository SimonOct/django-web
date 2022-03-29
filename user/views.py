
from django.shortcuts import redirect, render, HttpResponse
from . import models
# 用与urlencode和decode
from urllib import parse
# 用于生成随机数
import uuid
# 用于发送邮件
from django.core.mail import send_mail
# 用于反向解析urls.py内的路径
from django.urls import reverse
# 用于定制authenticate
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
# 用于用户登录和登出
from django.contrib.auth import logout as signout, login as signin

from django.contrib.auth.decorators import login_required

from django.utils import timezone
# Create your views here.


# 定制authenticate方法，使其支持用邮箱或者用户名登录
class CustomBackend(ModelBackend):
    def authenticate(self, email=None, password=None, **kwargs):
        try:
            user = models.UserRegistration.objects.get(
                Q(username=email, email_is_verified=True) | Q(email=email, email_is_verified=True) | Q(username=email, repairEmployee=True) )
            if user.check_password(password):
                return user
        except Exception as e:
            return None

# 注册用户
def registration(request):
    # 如果请求方式是GET，则返回一个注册页面
    if request.method == 'GET':
        return render(request, 'user/registration.html')

    elif request.method == 'POST':
        # 获取客户在注册页面提交的所有数据
        email = request.POST['email']
        user_name = request.POST['user_name']
        user_password = request.POST['user_password']
        user_registration_to_school = request.POST['user_registration_to_school']
        campus = request.POST['campus']
        dormitoryA = request.POST['dormitoryA']
        dormitoryB = request.POST['dormitoryB']
        user_sex = request.POST.get('user_sex', '')
        user_birthday = request.POST.get('user_birthday', '')

        # 将存在数据库中尚未使用的链接删除，以便重新发送验证邮箱
        try:
            alredy_code = models.EmailValidation.objects.filter(email=email)
            alredy_code.delete()
        except:
            pass
        try:
            alredy_email = models.UserRegistration.objects.get(email=email)
            alredy_email.delete()
        except:
            pass

        # 生成一个随机数用于验证邮箱
        try:
            random_code = uuid.uuid4()
            models.EmailValidation.objects.create(
                email=email, email_code=random_code)
        except:
            return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
        # 将邮箱进行格式化,方便用户打开
        encode_email = parse.quote(email)
        url = reverse('user:emailvalidation')
        domain = 'http://127.0.0.1'
        context = f'点击下方链接验证邮箱: \n{domain}{url}?uuid={random_code}&email={encode_email}'
        # 发送邮件
        send_mail('注册链接', context, 'example@example.com',
                  [email], fail_silently=False,)
        # 创建用户, 此处用try是为了防止数据插入时出现意料之外的错误
        try:
            user = models.UserRegistration.objects.create_user(
                user_name, email, user_password)
            user.email_is_verified = False
            user.registration_to_school = user_registration_to_school
            user.campus = campus
            user.dormitoryA = dormitoryA
            user.dormitoryB = dormitoryB
            user.sex = user_sex
            user.birthday = user_birthday
            user.save()
            return redirect(reverse('user:login'))
        except:
            pass
    
    return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

    

# 检查邮箱或用户名是否有重复, 配合注册页面的Ajax, 如果存在相同则返回状态码404, 不存在则返回200
def checkDuplicate(request):
    email = request.GET.get('email', False)
    username = request.GET.get('username', False)
    if email:
        # 将经过转换的邮箱地址转换成正常的地址
        email = parse.unquote(email)
        # 在数据库中查询是否存在一个已经验证过的相同邮箱
        try:
            models.UserRegistration.objects.get(
                email=email, email_is_verified=True)
            return HttpResponse(status=404)
        except:
            pass
    if username:
        # 将经过转换的用户名地址转换成正常的用户名
        username = parse.unquote(username)
        # 在数据库中查询是否存在一个已经验证过的相同用户名或拥有管理权限的账户.
        try:
            models.UserRegistration.objects.get(
                username=username, email_is_verified=True)
            return HttpResponse(status=404)
        except:
            pass
        try:
            models.UserRegistration.objects.get(
                username=username, is_staff=True)
            return HttpResponse(status=404)
        except:
            pass
        try:
            models.UserRegistration.objects.get(
                username=username, is_superuser=True)
            return HttpResponse(status=404)
        except:
            pass
    return HttpResponse(status=200)

# 用于验证邮箱有效性
def emailValidation(request):
    uuid = request.GET.get('uuid')
    email = request.GET.get('email')
    email = parse.unquote(email)
    try:
        checked = models.EmailValidation.objects.get(
            email=email, email_code=uuid)
        checked.delete()
        turn_true = models.UserRegistration.objects.get(email=email)
        turn_true.email_is_verified = True
        turn_true.save()
        return redirect(reverse('user:login'))
    except:
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

# 用于用户登录
def login(request):
    if request.method == 'GET':
        next = request.GET.get('next', False)
        # 如果用户已经登录但还是要访问登录页面,则让其跳转到首页
        if request.user.is_authenticated:
            return redirect(reverse('index:index'))
        if next:
            # 如果是从其它页面跳转过来,则记录下原本访问的页面,并将信息传到登录页面中
            next_url = {"next_url": next}
            return render(request, 'user/login.html', next_url)
        next_url = {"next_url": '/'}
        return render(request, 'user/login.html', next_url)

    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    user = CustomBackend.authenticate(request, email=email, password=password)
    if user is not None:
        if request.POST.get('rememberMe', 'False') == 'True':
            # 设置客户端的session有效期为14天
            request.session.set_expiry(1_209_600)
        # 认证后端有多个，这里指定定制的后端。默认的后端用来admin页面的验证
        signin(request, user, backend='user.views.CustomBackend')
        # 从客户端传送过来的表单中提取原本访问的页面
        return redirect(request.POST.get('next_url', '/'))
    else:
        next = request.POST.get('next_url', '/')
        # 传送登录错误的信息
        warning = '<div class="alert alert-danger" role="alert">账号或密码错误</div>'
        content = {'msg': warning, "next_url": next}
        return render(request, 'user/login.html', content)

# 用于用户登出
def logout(request):
    signout(request)
    return redirect('/')

def forgot(request):
    if request.method == 'GET':
        return render(request, 'user/forgot.html')
    if request.method == 'POST':
        email = request.POST.get('email', False)
        if email == False:
            error = '<div class="alert alert-danger" role="alert">用户不存在!</div>'
            content = {'msg': error}
            return render(request, 'user/forgot.html', content)
        # 将存在数据库中尚未使用的链接删除，以便重新发送验证邮箱
        try:
            alredy_code = models.EmailCheck.objects.filter(email=email)
            alredy_code.delete()
        except:
            pass
        try:
            models.UserRegistration.objects.get(email=email, email_is_verified=True)
            random_code = uuid.uuid4()
            models.EmailCheck.objects.create(email=email, email_code=random_code)

            encode_email = parse.quote(email)
            url = reverse('user:reset')
            domain = 'http://127.0.0.1'
            context = f'点击下方链接重置密码: \n{domain}{url}?uuid={random_code}&email={encode_email}'
            # 发送邮件
            send_mail('重置密码', context, 'example@example.com',
                    [email], fail_silently=False,)
            success = '<div class="alert alert-success" role="alert">验证链接已发送!请检查邮箱</div>'
            content = {'msg': success}
            return render(request, 'user/forgot.html', content)
        except:
            error = '<div class="alert alert-danger" role="alert">用户不存在!</div>'
            content = {'msg': error}
            return render(request, 'user/forgot.html', content)
    return HttpResponse(status=404)

def reset(request):
    if request.method == 'GET':
        uuid = request.GET.get('uuid', False)
        email = request.GET.get('email', False)
        if uuid == False or email == False:
            return HttpResponse(status=404)
        try:
            # 将经过转换的邮箱地址转换成正常的地址
            email = parse.unquote(email)
            account = models.EmailCheck.objects.get(email=email)
            if account.email_code != uuid:
                return HttpResponse(status=404)
        except:
            return HttpResponse(status=404)
        content = {
            'email': email,
            'uuid': uuid
        }
        return render(request, 'user/reset.html', content)
        
    
    if request.method == 'POST':
        uuid = request.POST.get('uuid', False)
        email = request.POST.get('email', False)
        password = request.POST.get('password', False)

        if uuid == False or email == False or password == False:
            return HttpResponse(status=404)
        try:
            account = models.EmailCheck.objects.get(email=email)
            if account.email_code != uuid:
                return HttpResponse(status=404)
        except:
            return HttpResponse(status=404)

        u = models.UserRegistration.objects.get(email=email)
        u.set_password(password)
        u.save()
        account.delete()

        success = '<div class="alert alert-success" role="alert">密码更新成功</div>'
        content = {'msg': success, "next_url": reverse('index:index')}
        return render(request, 'user/login.html', content)

@login_required
def user_info(request):
    return render(request, 'user/user_info.html', locals())

@login_required
def email_change_code(request):
    if request.method == 'GET':
        email = request.GET.get('email', False)
        getCode = request.GET.get('getcode', False)
        uid = request.GET.get('uid')
        if email:
            alredy_code = models.EmailChange.objects.filter(user_id=uid)
            alredy_code.delete()
            try:
                code = str(uuid.uuid4())[:8]
                models.EmailChange.objects.create(email=email, email_code=code, user_id=request.user.id)
            except:
                return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
            
            context = f'验证码为：{code} （15分钟内有效）'
            send_mail('更换邮箱验证码', context, 'example@example.com',
                  [email], fail_silently=False,)
            return
        if getCode:
            try:
                check = models.EmailChange.objects.get(user_id=uid, email_code=getCode.lower())
                if (timezone.now() - check.create_time).total_seconds() > 900:
                    return HttpResponse('验证码错误', status=403)
                return HttpResponse(status=200)
            except:
                return HttpResponse('验证码错误', status=403)
    return HttpResponse(status=404)

@login_required
def change_user_info(request):
    if request.method == 'POST':
        email = request.POST.get('email', False)
        username = request.POST.get('username', False)
        sex = request.POST.get('sex', False)
        birthday = request.POST.get('birthday', False)
        if email:
            try:
                check = models.EmailChange.objects.get(email=email)
                code = request.POST['getCode']
                if code.lower() != check.email_code.lower():
                    return HttpResponse(status=404)
                if (timezone.now() - check.create_time).total_seconds() > 900:
                    return HttpResponse(status=404)
                check.delete()
                user = models.UserRegistration.objects.get(id=request.user.id)
                user.email = email
                user.save()
                return redirect(reverse('user:user_info'))
            except:
                pass 
        if username:
            try:
                user = models.UserRegistration.objects.get(id=request.user.id)
                user.username = username
                user.save()
                return HttpResponse(status=200)
            except:
                pass
        if sex:
            user = models.UserRegistration.objects.get(id=request.user.id)
            user.sex = sex
            user.save()
            return HttpResponse(status=200)
        if birthday:
            user = models.UserRegistration.objects.get(id=request.user.id)
            user.birthday = birthday
            user.save()
            return HttpResponse(status=200) 
    return HttpResponse(status=404)




    
