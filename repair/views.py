from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from urllib import parse
from .models import Campus, Dormitory
import re
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    return render(request, 'repair/index.html')

# 报告校园需要维修的页面
@login_required
def campusReport(request):
    if request.method == 'GET':
        return render(request, 'repair/campusReport.html')
    elif request.method == 'POST':
        if request.user.is_authenticated:
            creater_id = request.user.id
            campus = request.POST['campus']
            title = request.POST['title']
            buldding_name = request.POST['buildingradio']
            levelradio = request.POST['levelradio']
            description = request.POST.get('description')
            # 当数据插入出错时提示错误信息
            try:
                added = Campus.objects.create(creater_id=creater_id, campus=campus, title=title, buldding_name=buldding_name, levelradio=levelradio, description=description)
            except:
                return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
            # 仅将.jpg .jpeg .png .webp格式的文件保存, 就算用户上传了其它格式的文件也不报错但不保存
            picture = request.FILES.get('picture')
            reg = '^.*(\.jpg|\.jpeg|\.png|\.webp)$'
            match = re.search(reg, picture.name)
            if match:
                # 将图片名称进行URL编码
                picture.name = parse.quote(picture.name)
                added.picture = picture
                added.save()
                pass

            return redirect(reverse("repair:campuslist_id", kwargs={"campuslist_id": added.id}))

    return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

# 展示已经报告了校园需要维修的页面
# def campusReportList(request):
#     if request.method != 'GET':
#         return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
#     hpage_num = request.GET.get('hpage', 1)
#     bpage_num = request.GET.get('bpage', 1)
#     hcampuslist = Campus.objects.filter(campus='海珠校区').order_by('-date_added')
#     bcampuslist = Campus.objects.filter(campus='白云校区').order_by('-date_added')
#     p_hcampuslist = Paginator(hcampuslist, 10)
#     p_bcampuslist = Paginator(bcampuslist, 10)
#     # 当用户提交一个数值,并且该数值对应的分页没有内容,会报错,如http://127.0.0.1:8000/repair/campus/list/?bpage=200000
#     try:
#         c_hcampuslist_page = p_hcampuslist.page(int(hpage_num))
#         c_bcampuslist_page = p_bcampuslist.page(int(bpage_num))
#     except:
#         return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

#     context = {'hcampuslist': hcampuslist,
#                'bcampuslist': bcampuslist,
#                'p_hcampuslist': p_hcampuslist,
#                'p_bcampuslist': p_bcampuslist,
#                'c_hcampuslist_page': c_hcampuslist_page,
#                'c_bcampuslist_page': c_bcampuslist_page,
#                }
#     return render(request, 'repair/campusReportList.html', context)

# 展示已经报告了校园需要维修的页面-Ajax版
# 返回一个模板页面
def campusReportListTemplates(request):
    if request.method != 'GET':
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
    return render(request, 'repair/campusReportList_ajax.html')
# 模板页面加载完成后会发送两个请求，请求白云校区与海珠校区第一页的保修列表
# 海珠校区
def hcampusReportListAjax(request):
    # 如果不是GET请求则报错
    if request.method != 'GET':
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
    # 获取请求列表
    hpage_num = request.GET.get('hpage', 1)
    hcampuslist = Campus.objects.filter(campus='海珠校区').order_by('-date_added')
    h = Paginator(hcampuslist, 10)
    # 防止用户在浏览器通过url直接访问列表时填入不正确的分页数字
    try:
        c_hcampuslist_page = h.page(int(hpage_num))
    except:
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

    # 生成某个分页的报修列表
    hlist = ''
    for list in c_hcampuslist_page:
        if list.levelradio == '低':
            hlevel = '<span class="badge bg-secondary">低</span>'
            hlevel = str(hlevel)
        elif list.levelradio == '中':
            hlevel = '<span class="badge bg-warning text-dark">中</span>'
            hlevel = str(hlevel)
        elif list.levelradio == '高':
            hlevel = '<span class="badge bg-danger">高</span>'
            hlevel = str(hlevel)

        
        if list.done == False:
            hdone = '待处理🚗<br>'
            hdone = str(hdone)
        elif list.done == True:
            
            hdone = '已维修✔<br>'
            hdone = str(hdone)
        hlist = str(hlist)
        hlist += f'<a href="{reverse("repair:campuslist")}{list.id}" class="list-group-item list-group-item-action">{hlevel}{hdone}标题：{list.title}<br>地点：{list.buldding_name}<br>提交日期：{timezone.make_naive(list.date_added).strftime("%Y年%m月%d日 %H:%M:%S")}</a>'
    
    # 分页导航相关
    # 判断是否有上一页，如果有的话上一页按钮可用并且能正确导向上一页，否则显示效果为被禁用按钮的样式
    if c_hcampuslist_page.has_previous():
        hpage_previous = f'<li class="page-item"><button class="page-link" value="{reverse("repair:hlist")}?hpage={c_hcampuslist_page.previous_page_number()}" onclick="hpagination(this.value)" type="button">上一页</button></li>'
    else:
        hpage_previous = '<li class="page-item disabled"><button class="page-link" type="button">上一页</button></li>'
    # 生成具体页数，并且附上对应的值让按钮可用，但如果用户所处页面与某个导航数字相同，那么对应的按钮会显示为禁用
    # 智能分页，当分页数量过多时，会自动缩略，下面设置的范围是（如果太多）显示第一页和最后一页，中间部分显示10页
    page_range = h.get_elided_page_range(hpage_num, on_each_side=5, on_ends=1)
    hpage_nav = ''
    for p_num in page_range:
        if p_num == c_hcampuslist_page.number:
            hpage_nav = str(hpage_nav)
            hpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
        elif p_num == '…':
            hpage_nav = str(hpage_nav)
            hpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
        else:
            hpage_nav = str(hpage_nav)
            hpage_nav += f'<li class="page-item"><button class="page-link" value="{reverse("repair:hlist")}?hpage={p_num}" onclick="hpagination(this.value)" type="button">{p_num}</button></li>'
    if c_hcampuslist_page.has_next():
        hpage_next = f'<li class="page-item"><button class="page-link" value="{reverse("repair:hlist")}?hpage={c_hcampuslist_page.next_page_number()}" onclick="hpagination(this.value)" type="button">下一页</button></li>'
    else:
        hpage_next = '<li class="page-item disabled"><button class="page-link" type="button">下一页</button></li>'
    # 像积木一样拼接
    content = f'<div class="list-group">{hlist}</div><nav aria-label="Page navigation example"><ul class="pagination justify-content-center">{hpage_previous}{hpage_nav}{hpage_next}</ul></nav>'
    content = str(content)
    # 将拼接好的文本传输出去
    return HttpResponse(content)

def bcampusReportListAjax(request):
    # 如果不是GET请求则报错
    if request.method != 'GET':
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
    # 获取请求列表
    bpage_num = request.GET.get('bpage', 1)
    bcampuslist = Campus.objects.filter(campus='白云校区').order_by('-date_added')
    b = Paginator(bcampuslist, 10)
    # 防止用户在浏览器通过url直接访问列表时填入不正确的分页数字
    try:
        c_bcampuslist_page = b.page(int(bpage_num))
    except:
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

    # 生成某个分页的报修列表
    blist = ''
    for list in c_bcampuslist_page:
        if list.levelradio == '低':
            blevel = '<span class="badge bg-secondary">低</span>'
            blevel = str(blevel)
        elif list.levelradio == '中':
            blevel = '<span class="badge bg-warning text-dark">中</span>'
            blevel = str(blevel)
        elif list.levelradio == '高':
            blevel = '<span class="badge bg-danger">高</span>'
            blevel = str(blevel)

        
        if list.done == False:
            bdone = '待处理🚗<br>'
            bdone = str(bdone)
        elif list.done == True:
            
            bdone = '已维修✔<br>'
            bdone = str(bdone)
        blist = str(blist)
        blist += f'<a href="{reverse("repair:campuslist")}{list.id}" class="list-group-item list-group-item-action">{blevel}{bdone}标题：{list.title}<br>地点：{list.buldding_name}<br>提交日期：{timezone.make_naive(list.date_added).strftime("%Y年%m月%d日 %H:%M:%S")}</a>'
        
    # 分页导航相关
    # 判断是否有上一页，如果有的话上一页按钮可用并且能正确导向上一页，否则显示效果为被禁用按钮的样式
    if c_bcampuslist_page.has_previous():
        bpage_previous = f'<li class="page-item"><button class="page-link" value="{reverse("repair:blist")}?bpage={c_bcampuslist_page.previous_page_number()}" onclick="bpagination(this.value)" type="button">上一页</button></li>'
    else:
        bpage_previous = '<li class="page-item disabled"><button class="page-link" type="button">上一页</button></li>'
    
    # 生成具体页数，并且附上对应的值让按钮可用，但如果用户所处页面与某个导航数字相同，那么对应的按钮会显示为禁用
    # 智能分页，当分页数量过多时，会自动缩略，下面设置的范围是（如果太多）显示第一页和最后一页，中间部分显示10页
    page_range = b.get_elided_page_range(bpage_num, on_each_side=5, on_ends=1)
    bpage_nav = ''
    for p_num in page_range:
        if p_num == c_bcampuslist_page.number:
            bpage_nav = str(bpage_nav)
            bpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
        elif p_num == '…':
            bpage_nav = str(bpage_nav)
            bpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
        else:
            bpage_nav = str(bpage_nav)
            bpage_nav += f'<li class="page-item"><button class="page-link" value="{reverse("repair:blist")}?bpage={p_num}" onclick="bpagination(this.value)" type="button">{p_num}</button></li>'
    if c_bcampuslist_page.has_next():
        bpage_next = f'<li class="page-item"><button class="page-link" value="{reverse("repair:blist")}?bpage={c_bcampuslist_page.next_page_number()}" onclick="bpagination(this.value)" type="button">下一页</button></li>'
    else:
        bpage_next = '<li class="page-item disabled"><button class="page-link" type="button">下一页</button></li>'
    
    # 像积木一样拼接
    content = f'<div class="list-group">{blist}</div><nav aria-label="Page navigation example"><ul class="pagination justify-content-center">{bpage_previous}{bpage_nav}{bpage_next}</ul></nav>'
    content = str(content)
    # 将拼接好的文本传输出去
    return HttpResponse(content)

# 展示某个报告的具体内容
@login_required
def campusReportListId(request, campuslist_id):
    # 将接收到的campuslist_id当作条件在数据库中查询
    campuslist_id = Campus.objects.get(id = campuslist_id)
    # 如果访问的方法为POST请求，并且提交POST请求的账号属于维修人员账号则将是否已处理设置为True，维修者id设置为维修人员账号的id
    if request.method == 'POST' and request.user.repairEmployee == True:
        campuslist_id.done = True
        campuslist_id.operater_id = request.user.id
        campuslist_id.save()
    content = {'detailed': campuslist_id}
    return render(request, 'repair/campusReportListId.html', content)

# 给维修人员专门展示尚未维修的校园报修信息
@login_required
def repairEmployeeList(request):
    try:
        if request.user.repairEmployee:
            return render(request, 'repair/campusEmployeeReportList.html')
    except:
        pass
    return HttpResponse(status=404)

@login_required
def hrepairEmployeeListAjax(request):
    if request.user.repairEmployee:
        hpage_num = request.GET.get('hpage', 1)
        hcampuslist = Campus.objects.filter(campus='海珠校区', done=False).order_by('date_added')
        h = Paginator(hcampuslist, 10)
        # 防止用户在浏览器通过url直接访问列表时填入不正确的分页数字
        try:
            c_hcampuslist_page = h.page(int(hpage_num))
        except:
            return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

        # 生成某个分页的报修列表
        hlist = ''
        for list in c_hcampuslist_page:
            if list.levelradio == '低':
                hlevel = '<span class="badge bg-secondary">低</span>'
                hlevel = str(hlevel)
            elif list.levelradio == '中':
                hlevel = '<span class="badge bg-warning text-dark">中</span>'
                hlevel = str(hlevel)
            elif list.levelradio == '高':
                hlevel = '<span class="badge bg-danger">高</span>'
                hlevel = str(hlevel)

            
            if list.done == False:
                hdone = '待处理🚗<br>'
                hdone = str(hdone)
            elif list.done == True:
                
                hdone = '已维修✔<br>'
                hdone = str(hdone)
            hlist = str(hlist)
            hlist += f'<a href="{reverse("repair:campuslist")}{list.id}" class="list-group-item list-group-item-action">{hlevel}{hdone}标题：{list.title}<br>地点：{list.buldding_name}<br>提交日期：{timezone.make_naive(list.date_added).strftime("%Y年%m月%d日 %H:%M:%S")}</a>'
        
        # 分页导航相关
        # 判断是否有上一页，如果有的话上一页按钮可用并且能正确导向上一页，否则显示效果为被禁用按钮的样式
        if c_hcampuslist_page.has_previous():
            hpage_previous = f'<li class="page-item"><button class="page-link" value="{reverse("repair:hlistforrepair")}?hpage={c_hcampuslist_page.previous_page_number()}" onclick="hpagination(this.value)" type="button">上一页</button></li>'
        else:
            hpage_previous = '<li class="page-item disabled"><button class="page-link" type="button">上一页</button></li>'
        # 生成具体页数，并且附上对应的值让按钮可用，但如果用户所处页面与某个导航数字相同，那么对应的按钮会显示为禁用
        # 智能分页，当分页数量过多时，会自动缩略，下面设置的范围是（如果太多）显示第一页和最后一页，中间部分显示10页
        page_range = h.get_elided_page_range(hpage_num, on_each_side=5, on_ends=1)
        hpage_nav = ''
        for p_num in page_range:
            if p_num == c_hcampuslist_page.number:
                hpage_nav = str(hpage_nav)
                hpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
            elif p_num == '…':
                hpage_nav = str(hpage_nav)
                hpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
            else:
                hpage_nav = str(hpage_nav)
                hpage_nav += f'<li class="page-item"><button class="page-link" value="{reverse("repair:hlistforrepair")}?hpage={p_num}" onclick="hpagination(this.value)" type="button">{p_num}</button></li>'
        if c_hcampuslist_page.has_next():
            hpage_next = f'<li class="page-item"><button class="page-link" value="{reverse("repair:hlistforrepair")}?hpage={c_hcampuslist_page.next_page_number()}" onclick="hpagination(this.value)" type="button">下一页</button></li>'
        else:
            hpage_next = '<li class="page-item disabled"><button class="page-link" type="button">下一页</button></li>'
        # 像积木一样拼接
        content = f'<div class="list-group">{hlist}</div><nav aria-label="Page navigation example"><ul class="pagination justify-content-center">{hpage_previous}{hpage_nav}{hpage_next}</ul></nav>'
        content = str(content)
        # 将拼接好的文本传输出去
        return HttpResponse(content)

    return HttpResponse(status=404)

@login_required
def brepairEmployeeListAjax(request):
    if request.user.repairEmployee:
        bpage_num = request.GET.get('bpage', 1)
        bcampuslist = Campus.objects.filter(campus='白云校区', done=False).order_by('date_added')
        b = Paginator(bcampuslist, 10)
        # 防止用户在浏览器通过url直接访问列表时填入不正确的分页数字
        try:
            c_bcampuslist_page = b.page(int(bpage_num))
        except:
            return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

        # 生成某个分页的报修列表
        blist = ''
        for list in c_bcampuslist_page:
            if list.levelradio == '低':
                blevel = '<span class="badge bg-secondary">低</span>'
                blevel = str(blevel)
            elif list.levelradio == '中':
                blevel = '<span class="badge bg-warning text-dark">中</span>'
                blevel = str(blevel)
            elif list.levelradio == '高':
                blevel = '<span class="badge bg-danger">高</span>'
                blevel = str(blevel)

            
            if list.done == False:
                bdone = '待处理🚗<br>'
                bdone = str(bdone)
            elif list.done == True:
                
                bdone = '已维修✔<br>'
                bdone = str(bdone)
            blist = str(blist)
            blist += f'<a href="{reverse("repair:campuslist")}{list.id}" class="list-group-item list-group-item-action">{blevel}{bdone}标题：{list.title}<br>地点：{list.buldding_name}<br>提交日期：{timezone.make_naive(list.date_added).strftime("%Y年%m月%d日 %H:%M:%S")}</a>'
            
        # 分页导航相关
        # 判断是否有上一页，如果有的话上一页按钮可用并且能正确导向上一页，否则显示效果为被禁用按钮的样式
        if c_bcampuslist_page.has_previous():
            bpage_previous = f'<li class="page-item"><button class="page-link" value="{reverse("repair:blistforrepair")}?bpage={c_bcampuslist_page.previous_page_number()}" onclick="bpagination(this.value)" type="button">上一页</button></li>'
        else:
            bpage_previous = '<li class="page-item disabled"><button class="page-link" type="button">上一页</button></li>'
        
        # 生成具体页数，并且附上对应的值让按钮可用，但如果用户所处页面与某个导航数字相同，那么对应的按钮会显示为禁用
        # 智能分页，当分页数量过多时，会自动缩略，下面设置的范围是（如果太多）显示第一页和最后一页，中间部分显示10页
        page_range = b.get_elided_page_range(bpage_num, on_each_side=5, on_ends=1)
        bpage_nav = ''
        for p_num in page_range:
            if p_num == c_bcampuslist_page.number:
                bpage_nav = str(bpage_nav)
                bpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
            elif p_num == '…':
                bpage_nav = str(bpage_nav)
                bpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
            else:
                bpage_nav = str(bpage_nav)
                bpage_nav += f'<li class="page-item"><button class="page-link" value="{reverse("repair:blistforrepair")}?bpage={p_num}" onclick="bpagination(this.value)" type="button">{p_num}</button></li>'
        if c_bcampuslist_page.has_next():
            bpage_next = f'<li class="page-item"><button class="page-link" value="{reverse("repair:blistforrepair")}?bpage={c_bcampuslist_page.next_page_number()}" onclick="bpagination(this.value)" type="button">下一页</button></li>'
        else:
            bpage_next = '<li class="page-item disabled"><button class="page-link" type="button">下一页</button></li>'
        
        # 像积木一样拼接
        content = f'<div class="list-group">{blist}</div><nav aria-label="Page navigation example"><ul class="pagination justify-content-center">{bpage_previous}{bpage_nav}{bpage_next}</ul></nav>'
        content = str(content)
        # 将拼接好的文本传输出去
        return HttpResponse(content)

    return HttpResponse(status=404)

# 宿舍报修
@login_required
def dormitoryReport(request):
    if request.method == 'GET':
        return render(request, 'repair/dormitoryReport.html')
    elif request.method == 'POST':
        if request.user.is_authenticated:
            creater_id = request.user.id
            campus = request.POST['campus']
            title = request.POST['title']
            buldding_name = request.POST['buildingradio']
            dormitory_num = request.POST['dormitoryNumber']
            levelradio = request.POST['levelradio']
            description = request.POST.get('description')
            # 当数据插入出错时提示错误信息
            try:
                added = Dormitory.objects.create(creater_id=creater_id, campus=campus, title=title, buldding_name=buldding_name, dormitory_number=dormitory_num, levelradio=levelradio, description=description)
            except:
                return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
            # 仅将.jpg .jpeg .png .webp格式的文件保存, 就算用户上传了其它格式的文件也不报错但不保存
            picture = request.FILES.get('picture')
            reg = '^.*(\.jpg|\.jpeg|\.png|\.webp)$'
            match = re.search(reg, picture.name)
            if match:
                added.picture = picture
                added.save()
                pass

            return redirect(reverse("repair:dormitorylist_id", kwargs={"dormitorylist_id": added.id}))

# 返回一个模板页面
@login_required
def dormitoryReportListTemplates(request):
    if request.method != 'GET':
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
    return render(request, 'repair/dormitoryReportList_ajax.html')

def hdormitoryReportListAjax(request):
    # 如果不是GET请求则报错
    if request.method != 'GET':
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

    # 获取请求列表
    hpage_num = request.GET.get('hpage', 1)
    hdormitorylist = Dormitory.objects.filter(campus='海珠校区', creater_id=request.user.id).order_by('-date_added')
    h = Paginator(hdormitorylist, 10)
    # 防止用户在浏览器通过url直接访问列表时填入不正确的分页数字
    try:
        c_hdormitorylist_page = h.page(int(hpage_num))
    except:
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

    # 生成某个分页的报修列表
    hlist = ''
    for list in c_hdormitorylist_page:
        if list.levelradio == '低':
            hlevel = '<span class="badge bg-secondary">低</span>'
            hlevel = str(hlevel)
        elif list.levelradio == '中':
            hlevel = '<span class="badge bg-warning text-dark">中</span>'
            hlevel = str(hlevel)
        elif list.levelradio == '高':
            hlevel = '<span class="badge bg-danger">高</span>'
            hlevel = str(hlevel)

        
        if list.done == False:
            hdone = '待处理🚗<br>'
            hdone = str(hdone)
        elif list.done == True:
            
            hdone = '已维修✔<br>'
            hdone = str(hdone)
        hlist = str(hlist)
        hlist += f'<a href="{reverse("repair:dormitorylist")}{list.id}" class="list-group-item list-group-item-action">{hlevel}{hdone}标题：{list.title}<br>地点：{list.buldding_name}<br>提交日期：{timezone.make_naive(list.date_added).strftime("%Y年%m月%d日 %H:%M:%S")}</a>'
    
    # 分页导航相关
    # 判断是否有上一页，如果有的话上一页按钮可用并且能正确导向上一页，否则显示效果为被禁用按钮的样式
    if c_hdormitorylist_page.has_previous():
        hpage_previous = f'<li class="page-item"><button class="page-link" value="{reverse("repair:hdormitory")}?hpage={c_hdormitorylist_page.previous_page_number()}" onclick="hpagination(this.value)" type="button">上一页</button></li>'
    else:
        hpage_previous = '<li class="page-item disabled"><button class="page-link" type="button">上一页</button></li>'
    # 生成具体页数，并且附上对应的值让按钮可用，但如果用户所处页面与某个导航数字相同，那么对应的按钮会显示为禁用
    # 智能分页，当分页数量过多时，会自动缩略，下面设置的范围是（如果太多）显示第一页和最后一页，中间部分显示10页
    page_range = h.get_elided_page_range(hpage_num, on_each_side=5, on_ends=1)
    hpage_nav = ''
    for p_num in page_range:
        if p_num == c_hdormitorylist_page.number:
            hpage_nav = str(hpage_nav)
            hpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
        elif p_num == '…':
            hpage_nav = str(hpage_nav)
            hpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
        else:
            hpage_nav = str(hpage_nav)
            hpage_nav += f'<li class="page-item"><button class="page-link" value="{reverse("repair:hdormitory")}?hpage={p_num}" onclick="hpagination(this.value)" type="button">{p_num}</button></li>'
    if c_hdormitorylist_page.has_next():
        hpage_next = f'<li class="page-item"><button class="page-link" value="{reverse("repair:hdormitory")}?hpage={c_hdormitorylist_page.next_page_number()}" onclick="hpagination(this.value)" type="button">下一页</button></li>'
    else:
        hpage_next = '<li class="page-item disabled"><button class="page-link" type="button">下一页</button></li>'
    # 像积木一样拼接
    content = f'<div class="list-group">{hlist}</div><nav aria-label="Page navigation example"><ul class="pagination justify-content-center">{hpage_previous}{hpage_nav}{hpage_next}</ul></nav>'
    content = str(content)
    # 将拼接好的文本传输出去
    return HttpResponse(content)

@login_required
def bdormitoryReportListAjax(request):
    # 如果不是GET请求则报错
    if request.method != 'GET':
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)
    # 获取请求列表
    bpage_num = request.GET.get('bpage', 1)
    bdormitorylist = Dormitory.objects.filter(campus='白云校区', creater_id=request.user.id).order_by('-date_added')
    b = Paginator(bdormitorylist, 10)
    # 防止用户在浏览器通过url直接访问列表时填入不正确的分页数字
    try:
        c_bdormitorylist_page = b.page(int(bpage_num))
    except:
        return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

    # 生成某个分页的报修列表
    blist = ''
    for list in c_bdormitorylist_page:
        if list.levelradio == '低':
            blevel = '<span class="badge bg-secondary">低</span>'
            blevel = str(blevel)
        elif list.levelradio == '中':
            blevel = '<span class="badge bg-warning text-dark">中</span>'
            blevel = str(blevel)
        elif list.levelradio == '高':
            blevel = '<span class="badge bg-danger">高</span>'
            blevel = str(blevel)

        
        if list.done == False:
            bdone = '待处理🚗<br>'
            bdone = str(bdone)
        elif list.done == True:
            
            bdone = '已维修✔<br>'
            bdone = str(bdone)
        blist = str(blist)
        blist += f'<a href="{reverse("repair:dormitorylist")}{list.id}" class="list-group-item list-group-item-action">{blevel}{bdone}标题：{list.title}<br>地点：{list.buldding_name}<br>提交日期：{timezone.make_naive(list.date_added).strftime("%Y年%m月%d日 %H:%M:%S")}</a>'
        
    # 分页导航相关
    # 判断是否有上一页，如果有的话上一页按钮可用并且能正确导向上一页，否则显示效果为被禁用按钮的样式
    if c_bdormitorylist_page.has_previous():
        bpage_previous = f'<li class="page-item"><button class="page-link" value="{reverse("repair:bdormitory")}?bpage={c_bdormitorylist_page.previous_page_number()}" onclick="bpagination(this.value)" type="button">上一页</button></li>'
    else:
        bpage_previous = '<li class="page-item disabled"><button class="page-link" type="button">上一页</button></li>'
    
    # 生成具体页数，并且附上对应的值让按钮可用，但如果用户所处页面与某个导航数字相同，那么对应的按钮会显示为禁用
    # 智能分页，当分页数量过多时，会自动缩略，下面设置的范围是（如果太多）显示第一页和最后一页，中间部分显示10页
    page_range = b.get_elided_page_range(bpage_num, on_each_side=5, on_ends=1)
    bpage_nav = ''
    for p_num in page_range:
        if p_num == c_bdormitorylist_page.number:
            bpage_nav = str(bpage_nav)
            bpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
        elif p_num == '…':
            bpage_nav = str(bpage_nav)
            bpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
        else:
            bpage_nav = str(bpage_nav)
            bpage_nav += f'<li class="page-item"><button class="page-link" value="{reverse("repair:bdormitory")}?bpage={p_num}" onclick="bpagination(this.value)" type="button">{p_num}</button></li>'
    if c_bdormitorylist_page.has_next():
        bpage_next = f'<li class="page-item"><button class="page-link" value="{reverse("repair:bdormitory")}?bpage={c_bdormitorylist_page.next_page_number()}" onclick="bpagination(this.value)" type="button">下一页</button></li>'
    else:
        bpage_next = '<li class="page-item disabled"><button class="page-link" type="button">下一页</button></li>'
    
    # 像积木一样拼接
    content = f'<div class="list-group">{blist}</div><nav aria-label="Page navigation example"><ul class="pagination justify-content-center">{bpage_previous}{bpage_nav}{bpage_next}</ul></nav>'
    content = str(content)
    # 将拼接好的文本传输出去
    return HttpResponse(content)

# 展示某个报告的具体内容
def dormitoryReportListId(request, dormitorylist_id):
    # 将接收到的dormitorylist_id当作条件在数据库中查询
    dormitorylist_id = Dormitory.objects.get(id = dormitorylist_id)
    # 如果访问的方法为POST请求，并且提交POST请求的账号属于维修人员账号则将是否已处理设置为True，维修者id设置为维修人员账号的id
    if request.method == 'POST' and request.user.repairEmployee == True:
        dormitorylist_id.done = True
        dormitorylist_id.operater_id = request.user.id
        dormitorylist_id.save()
    content = {'detailed': dormitorylist_id}
    return render(request, 'repair/dormitoryReportListId.html', content)

# 给维修人员专门展示尚未维修的宿舍报修信息
@login_required
def dormitoryRepairEmployeeList(request):

    if request.user.repairEmployee:
        return render(request, 'repair/dormitoryEmployeeReportList.html')

    return HttpResponse(status=404)

@login_required
def hdormitoryRepairEmployeeList(request):
    if request.user.repairEmployee:
        hpage_num = request.GET.get('hpage', 1)
        hdormitorylist = Dormitory.objects.filter(campus='海珠校区', done=False).order_by('date_added')
        h = Paginator(hdormitorylist, 10)
        # 防止用户在浏览器通过url直接访问列表时填入不正确的分页数字
        try:
            c_hdormitorylist_page = h.page(int(hpage_num))
        except:
            return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

        # 生成某个分页的报修列表
        hlist = ''
        for list in c_hdormitorylist_page:
            if list.levelradio == '低':
                hlevel = '<span class="badge bg-secondary">低</span>'
                hlevel = str(hlevel)
            elif list.levelradio == '中':
                hlevel = '<span class="badge bg-warning text-dark">中</span>'
                hlevel = str(hlevel)
            elif list.levelradio == '高':
                hlevel = '<span class="badge bg-danger">高</span>'
                hlevel = str(hlevel)

            
            if list.done == False:
                hdone = '待处理🚗<br>'
                hdone = str(hdone)
            elif list.done == True:
                
                hdone = '已维修✔<br>'
                hdone = str(hdone)
            hlist = str(hlist)
            hlist += f'<a href="{reverse("repair:dormitorylist")}{list.id}" class="list-group-item list-group-item-action">{hlevel}{hdone}标题：{list.title}<br>地点：{list.buldding_name}<br>提交日期：{timezone.make_naive(list.date_added).strftime("%Y年%m月%d日 %H:%M:%S")}</a>'
        
        # 分页导航相关
        # 判断是否有上一页，如果有的话上一页按钮可用并且能正确导向上一页，否则显示效果为被禁用按钮的样式
        if c_hdormitorylist_page.has_previous():
            hpage_previous = f'<li class="page-item"><button class="page-link" value="{reverse("repair:hdormitoryforrepair")}?hpage={c_hdormitorylist_page.previous_page_number()}" onclick="hpagination(this.value)" type="button">上一页</button></li>'
        else:
            hpage_previous = '<li class="page-item disabled"><button class="page-link" type="button">上一页</button></li>'
        # 生成具体页数，并且附上对应的值让按钮可用，但如果用户所处页面与某个导航数字相同，那么对应的按钮会显示为禁用
        # 智能分页，当分页数量过多时，会自动缩略，下面设置的范围是（如果太多）显示第一页和最后一页，中间部分显示10页
        page_range = h.get_elided_page_range(hpage_num, on_each_side=5, on_ends=1)
        hpage_nav = ''
        for p_num in page_range:
            if p_num == c_hdormitorylist_page.number:
                hpage_nav = str(hpage_nav)
                hpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
            elif p_num == '…':
                hpage_nav = str(hpage_nav)
                hpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
            else:
                hpage_nav = str(hpage_nav)
                hpage_nav += f'<li class="page-item"><button class="page-link" value="{reverse("repair:hdormitoryforrepair")}?hpage={p_num}" onclick="hpagination(this.value)" type="button">{p_num}</button></li>'
        if c_hdormitorylist_page.has_next():
            hpage_next = f'<li class="page-item"><button class="page-link" value="{reverse("repair:hdormitoryforrepair")}?hpage={c_hdormitorylist_page.next_page_number()}" onclick="hpagination(this.value)" type="button">下一页</button></li>'
        else:
            hpage_next = '<li class="page-item disabled"><button class="page-link" type="button">下一页</button></li>'
        # 像积木一样拼接
        content = f'<div class="list-group">{hlist}</div><nav aria-label="Page navigation example"><ul class="pagination justify-content-center">{hpage_previous}{hpage_nav}{hpage_next}</ul></nav>'
        content = str(content)
        # 将拼接好的文本传输出去
        return HttpResponse(content)

    return HttpResponse(status=404)

@login_required
def bdormitoryRepairEmployeeList(request):
    if request.user.repairEmployee:
        bpage_num = request.GET.get('bpage', 1)
        bdormitorylist = Dormitory.objects.filter(campus='白云校区', done=False).order_by('date_added')
        b = Paginator(bdormitorylist, 10)
        # 防止用户在浏览器通过url直接访问列表时填入不正确的分页数字
        try:
            c_bdormitorylist_page = b.page(int(bpage_num))
        except:
            return HttpResponse('oooops,出现了错误,请稍后重试', status=403)

        # 生成某个分页的报修列表
        blist = ''
        for list in c_bdormitorylist_page:
            if list.levelradio == '低':
                blevel = '<span class="badge bg-secondary">低</span>'
                blevel = str(blevel)
            elif list.levelradio == '中':
                blevel = '<span class="badge bg-warning text-dark">中</span>'
                blevel = str(blevel)
            elif list.levelradio == '高':
                blevel = '<span class="badge bg-danger">高</span>'
                blevel = str(blevel)

            
            if list.done == False:
                bdone = '待处理🚗<br>'
                bdone = str(bdone)
            elif list.done == True:
                
                bdone = '已维修✔<br>'
                bdone = str(bdone)
            blist = str(blist)
            blist += f'<a href="{reverse("repair:dormitorylist")}{list.id}" class="list-group-item list-group-item-action">{blevel}{bdone}标题：{list.title}<br>地点：{list.buldding_name}<br>提交日期：{timezone.make_naive(list.date_added).strftime("%Y年%m月%d日 %H:%M:%S")}</a>'
            
        # 分页导航相关
        # 判断是否有上一页，如果有的话上一页按钮可用并且能正确导向上一页，否则显示效果为被禁用按钮的样式
        if c_bdormitorylist_page.has_previous():
            bpage_previous = f'<li class="page-item"><button class="page-link" value="{reverse("repair:bdormitoryforrepair")}?bpage={c_bdormitorylist_page.previous_page_number()}" onclick="bpagination(this.value)" type="button">上一页</button></li>'
        else:
            bpage_previous = '<li class="page-item disabled"><button class="page-link" type="button">上一页</button></li>'
        
        # 生成具体页数，并且附上对应的值让按钮可用，但如果用户所处页面与某个导航数字相同，那么对应的按钮会显示为禁用
        # 智能分页，当分页数量过多时，会自动缩略，下面设置的范围是（如果太多）显示第一页和最后一页，中间部分显示10页
        page_range = b.get_elided_page_range(bpage_num, on_each_side=5, on_ends=1)
        bpage_nav = ''
        for p_num in page_range:
            if p_num == c_bdormitorylist_page.number:
                bpage_nav = str(bpage_nav)
                bpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
            elif p_num == '…':
                bpage_nav = str(bpage_nav)
                bpage_nav += f'<li class="page-item disabled"><button class="page-link" disabled type="button">{p_num}</button></li>'
            else:
                bpage_nav = str(bpage_nav)
                bpage_nav += f'<li class="page-item"><button class="page-link" value="{reverse("repair:bdormitoryforrepair")}?bpage={p_num}" onclick="bpagination(this.value)" type="button">{p_num}</button></li>'
        if c_bdormitorylist_page.has_next():
            bpage_next = f'<li class="page-item"><button class="page-link" value="{reverse("repair:bdormitoryforrepair")}?bpage={c_bdormitorylist_page.next_page_number()}" onclick="bpagination(this.value)" type="button">下一页</button></li>'
        else:
            bpage_next = '<li class="page-item disabled"><button class="page-link" type="button">下一页</button></li>'
        
        # 像积木一样拼接
        content = f'<div class="list-group">{blist}</div><nav aria-label="Page navigation example"><ul class="pagination justify-content-center">{bpage_previous}{bpage_nav}{bpage_next}</ul></nav>'
        content = str(content)
        # 将拼接好的文本传输出去
        return HttpResponse(content)


    return HttpResponse(status=404)
