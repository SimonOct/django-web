from django.urls import path
from . import views

app_name = 'repair'

urlpatterns = [
    path('', views.index, name='index'),
    path('campus/', views.campusReport, name='campus'),
    # path('campus/list/', views.campusReportList, name='campuslist'),
    path('campus/list/<int:campuslist_id>', views.campusReportListId, name='campuslist_id'),

    path('campus/list/', views.campusReportListTemplates, name='campuslist'),
    path('campus/list/h', views.hcampusReportListAjax, name='hlist'),
    path('campus/list/b', views.bcampusReportListAjax, name='blist'),

    path('campus/listforrepair/', views.repairEmployeeList, name='list_for_repair'),
    path('campus/listforrepair/h', views.hrepairEmployeeListAjax, name='hlistforrepair'),
    path('campus/listforrepair/b', views.brepairEmployeeListAjax, name='blistforrepair'),

    path('dormitory/', views.dormitoryReport, name='dormitory'),
    path('dormitory/list/', views.dormitoryReportListTemplates, name='dormitorylist'),
    path('dormitory/list/h', views.hdormitoryReportListAjax, name='hdormitory'),
    path('dormitory/list/b', views.bdormitoryReportListAjax, name='bdormitory'),
    path('dormitory/list/<int:dormitorylist_id>', views.dormitoryReportListId, name='dormitorylist_id'),
    path('dormitory/listforrepair/', views.dormitoryRepairEmployeeList, name='dormitory_list_for_repair'),
    path('dormitory/listforrepair/h', views.hdormitoryRepairEmployeeList, name='hdormitoryforrepair'),
    path('dormitory/listforrepair/b', views.bdormitoryRepairEmployeeList, name='bdormitoryforrepair'),
]
