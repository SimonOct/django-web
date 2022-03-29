# 说明
django版本为3.2

在使用这个项目时，需要注意修改以下地方

注意，以下操作目录默认为项目的最外层目录

## 修改配置文件

### settings.py

打开`django_mysite/settings.py`

第24行，需要输入一个SECRET_KEY，[作用](https://docs.djangoproject.com/zh-hans/3.2/ref/settings/#std:setting-SECRET_KEY)

```python
SECRET_KEY = ''
```

第27行，默认值为Ture，用来开发时查看某些错误信息，但是如果需要部署到公网上就要让它为Fasle

```python
DEBUG = False
```

第30行，根据自己需要修改ip地址，[作用](https://docs.djangoproject.com/zh-hans/3.2/ref/settings/#allowed-hosts)

```python
ALLOWED_HOSTS = []
```

第87行，数据库相关，根据自己需求修改，下面的例子是使用mysql时的配置，[文档](https://docs.djangoproject.com/zh-hans/3.2/ref/databases/)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_mysite',
        'USER': 'django',
        'PASSWORD': 'Djang0_web',
        'HOST': 'localhost',
        'PORT': '3306',
        # 支持emoji
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

第154~159行，邮箱验证，按需修改，[文档](https://docs.djangoproject.com/zh-hans/3.2/ref/settings/#email-backend)

```python
EMAIL_USE_LOCALTIME = True
EMAIL_TIMEOUT = 10
EMAIL_PORT = 25
EMAIL_HOST = 'smtp.example.com'
EMAIL_HOST_USER = 'example@example.com'
EMAIL_HOST_PASSWORD = 'password_example'
```

### user/views.py

第75行与213行，邮箱验证相关，根据自身ip地址决定协议和具体的ip

```python
domain = 'http://127.0.0.1'
```

第78~79行、216~217行、291~292行，邮箱验证码发送，修改对应的邮箱地址

```python
        send_mail('注册链接', context, 'example@example.com',
                  [email], fail_silently=False,)
```

## 运行前准备

启动虚拟环境

```markdown
# linux用户
source django_web/bin/activate
# windows用户
.\django_web\bin\Activate.ps1
```

迁移数据

```bash
django-admin makemigrations

django-admin migrate
```

## 项目部署

WSGI(Web Server Gateway Interface) Web服务器网关接口, 是Python应用程序或框架和Web服务器之间的一种接口, 被广泛使用.

python manage.py runserver通常只在开发和测试环境中使用.

当开发结束后后, 完善的项目代码需要在一个高效稳定的环境中运行,这时可以使用WSGI

### uWSGI

- uWSGI是WSGI的一种,它实现了http协议,WSGI协议以及uWSGI协议.
- uWSGI功能完善,支持协议众多,在python web圈热度极高
- uWSGI主要以学习配置为主

在项目同名文件夹下添加配置文件

如`mysite/mysite/mysite.ini`

文件以[uwsgi]开头, 有如下配置项:

套接字方式 IP地址:端口号(需要nginx)

`socket=127.0.0.1:8000`

http通信方式 IP地址:端口号

`http=127.0.0.1:8000`

项目当前工作目录(绝对路径)

`chdir=.../mysite`

项目中wsgi.py文件的目录,相当于当前工作目录(相对路径，django3.2貌似不用这个)

`wsgi-file=my_project/wsgi.py`

进程个数

`process=4`

每个进程的线程个数

`threads=2`

服务的pid记录文件

`pidfile=uwsgi.pid`

服务的日志文件位置

`daemonize=uwsgi.log`

开启主进程管理模式

`master=true`

**Django的settings.py需要做如下配置**

- 修改settings.py,将DEBUG=True改为False
- 将ALLOWED_HOSTS=[]改为['网站域名']或相应的IP地址

启动uwsgi

cd到uWSGI配置文件所在目录

`uwsgi --ini 配置文件名.ini`

停止uwsgi

cd到uWSGI配置文件所在目录

`uwsgi --stop uwsgi.pid`

例子：

```shell
[uwsgi]
http=10.0.20.10:80
chdir=/usr/share/django_mysite/
module=django_mysite.wsgi:application
vacuum=True
harakiri=20
home=/usr/share/django_mysite/django_web/
process=1
threads=2
pidfile=uwsgi.pid
daemonize=uwsgi.log
master=True
env=DJANGO_SETTINGS_MODULE=django_mysite.settings
static-map=/static/bootstrap/=/usr/share/django_mysite/bootstrap/static/bootstrap/
```

### nginx

修改配置文件

`vim /etc/nginx/sites-enabled/default`

```shell
        location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                #try_files $uri $uri/ =404;
                uwsgi_pass 127.0.0.1:8000;
                include /etc/nginx/uwsgi_params;
        }
```

把uwsgi配置文件内的http改成socket，地址为127.0.0.1:8000，对应上面的nginx

```shell
socket=127.0.0.1:8000
```

完整：

```shell
[uwsgi]
socket=127.0.0.1:8000
chdir=/usr/share/django_mysite/
module=django_mysite.wsgi:application
vacuum=True
harakiri=20
home=/usr/share/django_mysite/django_web/
process=1
threads=2
pidfile=uwsgi.pid
daemonize=uwsgi.log
master=True
env=DJANGO_SETTINGS_MODULE=django_mysite.settings
py-autoreload=1
uid=1001
```

**静态文件配置**

```shell
        location /static/ {
                root /usr/share/django_mysite/bootstrap;
                autoindex o;
        }


        location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                #try_files $uri $uri/ =404;
                uwsgi_pass 127.0.0.1:8000;
                include /etc/nginx/uwsgi_params;
        }


        location /media/picture {
                root /usr/share/django_mysite;
                autoindex off;
        }
```

**更改文件上传大小限制**

`vim /etc/nginx/nginx.conf`

在http内添加 `client_max_body_size 12m`，12m代表12M，不添加的话默认为1M

## 最后

如果项目成功运行起来了，但是访问图片失败的话请先检查存储图片文件夹的权限

这个项目的许可

对于不是我实现的部分则根据其对应的开源协议处理

我所编写的部分采用的许可证为 MIT 协议
