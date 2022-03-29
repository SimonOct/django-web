from re import search
from django.contrib import admin
from .models import Campus, Dormitory
# Register your models here.
class CampusManager(admin.ModelAdmin):
    # 列表页显示哪些字段的列
    list_display = ['campus', 'title', 'buldding_name', 'levelradio', 'done', 'operater_id', 'date_added', 'date_update']
    # 控制list_display中的哪些字段可以连接到修改页
    list_display_links = ['title']
    # 过滤器，用来筛选的
    list_filter = ['campus', 'levelradio', 'done']
    # 添加搜索框(模糊查询)
    search_fields = ['title']
    # 添加可在列表页编辑的字段
    list_editable = ['done', 'operater_id']
    # 更多 https://docs.djangoproject.com/zh-hans/3.2/ref/contrib/admin/
class DormitoryManager(admin.ModelAdmin):
    # 列表页显示哪些字段的列
    list_display = ['campus', 'title', 'buldding_name', 'dormitory_number', 'levelradio', 'done', 'operater_id', 'date_added', 'date_update']
    # 控制list_display中的哪些字段可以连接到修改页
    list_display_links = ['title']
    # 过滤器，用来筛选的
    list_filter = ['campus', 'levelradio', 'done']
    # 添加搜索框(模糊查询)
    search_fields = ['title']
    # 添加可在列表页编辑的字段
    list_editable = ['done', 'operater_id']

admin.site.register(Campus, CampusManager)
admin.site.register(Dormitory, DormitoryManager)