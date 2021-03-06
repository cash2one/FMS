# coding=utf-8
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q, Count
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
import datetime, logging, time
from sale.models import *
from customer.models import *
from shande.util import *

logger = logging.getLogger("django")
@login_required()
def saleManage(request):
    # t1 = time.clock()
    if (not request.user.userprofile.title.role_name in ['admin', 'ops', 'saleboss']):
        return HttpResponseRedirect("/")
    bindUsers = User.objects.filter(userprofile__title__role_name='sale').order_by("username")
    if request.user.userprofile.title.role_name == 'saleboss':
        bindUsers = bindUsers.filter(userprofile__company=request.user.userprofile.company)
    bindTeachers = Teacher.objects.filter(binduser__isnull=False).order_by("teacherId")
    # for sale in Sale.objects.all():
    #     bindUsers = bindUsers.filter(~Q(id=sale.binduser.id))
    data = {
        "bindusers": bindUsers,
        "bindteachers": bindTeachers,
    }
    # t2 = time.clock()
    # logger.error("saleMange cost time: %f"%(t2-t1))
    return render(request, 'sale/saleManage.html', data)

@login_required()
def querySale(request):
    #查看权限：admin ops saleboss
    # t1 = time.clock()
    if(request.GET.get('saleid') or request.GET.get('department')
       or request.GET.get('binduser') or request.GET.get('bindteacher') or request.GET.get('msg')):
       sales = Sale.objects.all().order_by('saleId')
       #不同的用户看到不同的列表
       if request.user.userprofile.title.role_name == 'saleboss':
           sales = sales.filter(company=request.user.userprofile.company)

       sales = sales.filter(saleId__icontains=request.GET.get('saleid', ''))
       sales = sales.filter(company__icontains=request.GET.get('company', ''))
       sales = sales.filter(department__icontains=request.GET.get('department', ''))
       if 'binduser' in request.GET and request.GET['binduser'] != '':
           sales = sales.filter(binduser__userprofile__nick__icontains=request.GET.get('binduser'))
       if 'bindteacher' in request.GET and request.GET['bindteacher'] != '':
           sales = sales.filter(bindteacher__teacherId__icontains=request.GET.get('bindteacher'))
       if 'bindbursar' in request.GET and request.GET['bindbursar'] != '':
           sales = sales.filter(bindteacher__bindbursar__bursarId__icontains=request.GET.get('bindbursar'))

       p = Paginator(sales, 25)
       try:
           page = int(request.GET.get('page', '1'))
       except ValueError:
           page = 1
       try:
           salePage = p.page(page)
       except (EmptyPage, InvalidPage):
           salePage = p.page(p.num_pages)
       showContent = "True"
       showContent = json.dumps(showContent)
       data = {
           "salePage": salePage,
           "requestArgs": getArgsExcludePage(request),
           "showContent": showContent,
       }
    else:
        showContent = "False"
        showContent = json.dumps(showContent)
        data = {
            "showContent": showContent,
        }
    # t2 = time.clock()
    # logger.error("querySale cost time: %f" % (t2 - t1))
    return render(request, 'sale/querySale.html', data)

@login_required()
def addSale(request):
    # t1 = time.clock()
    data = {}
    try:
        if request.POST['id'] == "":#新建开发ID
            newSale = Sale.objects.create(saleId=request.POST['saleid'])
        else:#修改开发ID信息
            newSale = Sale.objects.get(id=request.POST['id'])
            newSale.saleId = request.POST['saleid']

        if request.POST.get('bindusername'):
            # binduserid = request.POST.get('binduser', '无')
            if User.objects.get(username=request.POST.get('bindusername','')):
                try:
                    user = User.objects.get(username=request.POST.get('bindusername'))
                    #若用户先前绑定了开发，则解绑
                    try:
                        oldSale = Sale.objects.get(binduser_id=str(user.id))
                        oldSale.binduser = None
                        oldSale.save()
                    except Exception as e:
                        pass
                    if newSale.company == user.userprofile.company:
                        newSale.binduser = user
                    # binduserid = str(user.id)
                    else:
                        raise Exception("开发和用户不属于同一公司")
                # binduserid = str(user.id)
                except Exception as e:
                    raise Exception("用户不存在")
        else:
            # binduserid = '无'
            newSale.binduser = None

        # if binduserid.isdigit():
        #     try:
        #         oldSale = Sale.objects.get(binduser_id=binduserid)
        #         oldSale.binduser = None
        #         oldSale.save()
        #     except Exception as e:
        #         # print(e.message)
        #         # print(e.__str__())
        #         pass
        #     if newSale.company == user.userprofile.company:
        #         newSale.binduser = user
        #         # binduserid = str(user.id)
        #     else:
        #         raise Exception("开发和用户不属于同一公司")
        # else:
        #     newSale.binduser = None

        #开发ID修改了绑定的真实用户 ，则更新所有相关的未提交客户真实开发用户信息
        customers = newSale.customer_set.filter(Q(status=0)|Q(status=10)|Q(status=30))
        for customer in customers:
            customer.realuser = newSale.binduser
            customer.save()
        #newSale.bindteacher = getTeacherBySaleId(request.POST['saleid'])
        # newSale.company = request.POST['company']
        # newSale.department = request.POST['department']


        teacherid = request.POST.get('bindteacherId', '')
        # teacher = Teacher.objects.get(teacherId=request.POST.get('bindteacherId', ''))
        if teacherid:
            teacher = Teacher.objects.get(teacherId=teacherid)
            if newSale.company == teacher.company:
                newSale.bindteacher = teacher
            else:
                raise Exception("开发人员和管理专员属于不同公司")
            # bindteacher = request.POST.get('bindteacher', '无')
            # bindteacher = str(teacher.id)
        else:
            # bindteacher = '无'
            newSale.bindteacher = None
        # if bindteacher.isdigit():
        #     # teacher = Teacher.objects.get(id=request.POST.get('bindteacher'))
        #     teacher = Teacher.objects.get(id=bindteacher)
        #     newSale.bindteacher = teacher
        # else:
        #     newSale.bindteacher = None

        #更换开发绑定的老师，将该开发所有的未提交的客户对应的老师都修改为新的老师
        # customers = newSale.customer_set.filter(Q(status=0)|Q(status=30)|Q(status=10))
        # for customer in customers:
        #     customer.teacher = newSale.bindteacher
        #     customer.save()
        newSale.save()
        data['msg'] = "操作成功"
        data['msgLevel'] = "info"
    except Exception as e:
        print(e.__str__())
        print(e.message)
        if str(e.__str__()).__contains__('saleId'):
            data['msg'] = "操作失败,开发ID已存在"
        elif str(e.__str__()).__contains__('binduser'):
            data['msg'] = "操作失败,用户已绑定开发，请刷新页面重试"
        else:
            data['msg'] = "操作失败,请联系管理员。错误信息:%s" % e.__str__()
        data['msgLevel'] = "error"
    # t2 = time.clock()
    # logger.error("addSale cost time: %f" % (t2 - t1))
    return HttpResponse(json.dumps(data))

@login_required()
def addSaleGroup(request):
    # t1 = time.clock()
    data = {}
    try:
        company = request.POST.get('saleCompany')
        department = request.POST.get('saleDepartment')
        group = request.POST.get('saleGroup')
        saleCount = request.POST.get('saleCount')

        #创建一个机器人Sale给非Sale添加的客户
        sale, created = Sale.objects.get_or_create(saleId='KF'+company+'888888',company=company)
        sale.save()

        # #创建一个机器人用户给机器人Sale绑定
        # newUser, created = User.objects.get_or_create(username='robert'+company,is_superuser=0,first_name='',
        #                                               last_name='',email='',is_starff=1,is_active=1,date_joined='')
        # newUser.set_password("123456")
        # newUser.userprofile.company = company
        # newUser.userprofile.failcount = 0
        # newUser.userpfofile.user = newUser
        # newUser.userprofile.commit = 0
        # newUser.userprofile.grade = 0
        #
        # newUser.save()


        for i in range(1, int(saleCount)+1):
            if i<10:
                index = '0' +str(i)
            else:
                index = str(i)
            saleId = 'KF'+ company + group + department + index
            sale, created = Sale.objects.get_or_create(saleId=saleId)
            sale.company = company
            sale.department = department
            sale.group = group
            sale.save()

        data['msg'] = "操作成功"
        data['msgLevel'] = "info"
    except Exception as e:
        print(e.__str__())
        if str(e.__str__()).__contains__('saleId'):
            data['msg'] = "操作失败,开发ID已存在"
        elif str(e.__str__()).__contains__('binduser'):
            data['msg'] = "操作失败,用户已绑定开发，请刷新页面重试"
        else:
            data['msg'] = "操作失败,请联系管理员。错误信息:%s" % e.__str__()
        data['msgLevel'] = "error"
    # t2 = time.clock()
    # logger.error("addSaleGroup cost time: %f" % (t2 - t1))
    return HttpResponse(json.dumps(data))

@login_required()
def delSale(request):
    data = {}
    try:
        tmpSale = Sale.objects.get(id=request.POST['id'])
        tmpSale.delete()
        data['msg'] = "操作成功"
        data['msgLevel'] = "info"
    except Exception as e:
        print(e.__str__())
        data['msg'] = "操作失败"
        data['msgLevel'] = "error"
    return HttpResponse(json.dumps(data))

@login_required()
def saleManagerPasswordManage(request):
    if (not request.user.userprofile.title.role_name in ['admin', 'ops', 'salemanager', 'saleboss']):
        return HttpResponseRedirect("/")
    passwordList = SaleManagerPassword.objects.all().order_by("company", "department")
    if request.user.userprofile.title.role_name in ['saleboss']:
        company = request.user.userprofile.company
        passwordList = passwordList.filter(company=company)
    elif request.user.userprofile.title.role_name in ['salemanager']:
        company = request.user.userprofile.company
        department = request.user.userprofile.department
        passwordList = passwordList.filter(company=company, department=department)
    else:
        passwordList = passwordList

    data = {
        "passwordList": passwordList,
    }
    return render(request, 'sale/saleManagerPasswordManage.html', data)

@login_required()
def addSaleManagerPassword(request):
    try:
        SaleManagerPassword.objects.create(company=request.POST.get('company'),
                                           department=request.POST.get('department'),
                                           password=request.POST.get('password'))
    except Exception as e:
        print(e.__str__())
        print(e.message)
    return HttpResponseRedirect('/sale/saleManagerPasswordManage')

@login_required()
def delSaleManagerPassword(request):
    try:
        SaleManagerPassword.objects.get(id=request.GET.get("id")).delete()
    except Exception as e:
        print(e.__str__())
        print(e.message)
    return HttpResponseRedirect('/sale/saleManagerPasswordManage')

@login_required()
def saleKpiReport(request):
    #查看权限：admin ops saleboss salemanager bursarmanager
    # t1 = time.clock()
    if (not request.user.userprofile.title.role_name in ['admin', 'ops', 'salemanager', 'saleboss','bursarmanager']):
        return HttpResponseRedirect("/")
    endDate = request.POST.get('endDate', "")
    if endDate == '':
        endDate = datetime.date.today() + datetime.timedelta(days=1)
    else:
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
    startDate = request.POST.get('startDate', "")
    if startDate == "":
        startDate = datetime.date.today()
    else:
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()

    if request.user.userprofile.title.role_name in ['admin', 'ops']:
        sql = """
            SELECT s.company, IFNULL(COUNT(c.id),0) as dcount
            FROM  sale_sale s
            LEFT JOIN customer_customer c ON c.sales_id = s.id and c.status = 40 and c.first_trade > '%s' and c.first_trade < '%s'
            GROUP BY s.company
            ORDER by dcount desc
        """ % (startDate, endDate)
    else:
        company = request.user.userprofile.company
        sql = """
            SELECT s.company, IFNULL(COUNT(c.id),0) as dcount
            FROM  sale_sale s
            LEFT JOIN customer_customer c ON c.sales_id = s.id and c.status = 40 and c.first_trade > '%s' and c.first_trade < '%s'
            WHERE s.company = '%s'
            GROUP BY s.company
            ORDER by dcount desc
        """ % (startDate, endDate,company)

    cursor = connection.cursor()
    cursor.execute(sql)
    companys = []
    # #不同角色看不到不同公司
    # if not request.user.userprofile.title.role_name in ['admin','ops']:
    #     for row in cursor.fetchall():
    #         company = {}
    #         if row[0] == request.user.userprofile.company:
    #             company['company'] = row[0]
    #             company['dcount'] = row[1]
    #             companys.append(company)
    # else:
    for row in cursor.fetchall():
        company = {}
        company['company'] = row[0]
        company['dcount'] = row[1]
        companys.append(company)

    count = 0
    for company in companys:
        count += 1
        if company['company'] == '':
            del companys[count-1]
            break

    data = {
        "companys": companys,
        "startDate": str(startDate),
        "endDate": str(endDate),
    }
    # t2 = time.clock()
    # logger.error("saleKpiReport cost time: %f" % (t2 - t1))
    return render(request, 'sale/saleKpiReport.html', data)

@login_required()
def getCompanyDetail(request):
    # t1 = time.clock()
    company = request.POST.get('company')
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    cursor = connection.cursor()
    cursor.execute("""
            SELECT s.department, IFNULL(COUNT(c.id),0) as dcount
            FROM  sale_sale s
            LEFT JOIN customer_customer c ON c.sales_id = s.id and c.status = 40 and c.first_trade > %s and c.first_trade < %s
            WHERE s.company = %s
            GROUP BY s.department
            ORDER by dcount desc, s.department
        """, [startDate, endDate, company])
    departments = []
    for row in cursor.fetchall():
        department = {}
        department['department'] = row[0]
        department['dcount'] = row[1]
        departments.append(department)
    data = {
        "departments": departments,
        "company": company,
        "startDate": str(startDate),
        "endDate": str(endDate),
    }
    # t2 = time.clock()
    # logger.error("getCompanyDetail cost time: %f" % (t2 - t1))
    return render(request, 'sale/getCompanyDetail.html', data)

@login_required()
def getDepartmentDetail(request):
    # t1 =time.clock()
    company = request.POST.get('company')
    department = request.POST.get('department')
    cursor = connection.cursor()
    cursor.execute("""
                SELECT s.group, IFNULL(COUNT(c.id),0) as dcount
                FROM  sale_sale s
                LEFT JOIN customer_customer c ON c.sales_id = s.id and c.status =40
                WHERE s.company = %s and s.department = %s
                GROUP BY s.group
                ORDER by dcount desc
            """, [company, department])
    groups = []
    for row in cursor.fetchall():
        group = {}
        group['group'] = row[0]
        group['dcount'] = row[1]
        groups.append(group)
    data = {
        "groups": groups,
        "company": company,
        "department": department,
    }
    # t2 = time.clock()
    # logger.error("getDepartmentDetail cost time: %f" % (t2 - t1))
    return render(request, 'sale/getDepartmentDetail.html', data)

@login_required()
def getDepartmentGroupDetail(request):
    # t1 =time.clock()
    company = request.POST.get('company')
    department = request.POST.get('department')
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    cursor = connection.cursor()
    cursor.execute("""
                SELECT s.id, s.saleid, IFNULL(COUNT(c.id),0) as dcount
                FROM  sale_sale s
                LEFT JOIN customer_customer c ON c.sales_id = s.id and c.status = 40 and c.first_trade > %s and c.first_trade < %s
                WHERE s.company = %s and s.department = %s and s.binduser_id is not null
                GROUP BY s.saleid
                ORDER by s.group, s.saleid
            """, [startDate, endDate, company, department])
    sales = []
    for row in cursor.fetchall():
        sale = {}
        sale['id'] = row[0]
        sale['sale'] = row[1]
        sale['dcount'] = row[2]
        sales.append(sale)
    data = {
        "sales": sales,
        "company": company,
        "department": department,
        "startDate": str(startDate),
        "endDate": str(endDate),
    }
    # t2 = time.clock()
    # logger.error("getDepartmentGroupDetail cost time: %f" % (t2 - t1))
    return render(request, 'sale/getDepartmentGroupDetail.html', data)

@login_required()
def getGroupDetail(request):
    # t1 = time.clock()
    company = request.POST.get('company')
    department = request.POST.get('department')
    group = request.POST.get('group')
    cursor = connection.cursor()
    cursor.execute("""
                SELECT s.id, s.saleid, IFNULL(COUNT(c.id),0) as dcount
                FROM  sale_sale s
                LEFT JOIN customer_customer c ON c.sales_id = s.id and c.status = 40
                WHERE s.company = %s and s.department = %s and s.group = %s
                GROUP BY s.saleid
                ORDER by dcount desc
            """, [company, department, group])
    sales = []
    for row in cursor.fetchall():
        sale = {}
        sale['id'] = row[0]
        sale['sale'] = row[1]
        sale['dcount'] = row[2]
        sales.append(sale)
    data = {
        "sales": sales,
        "group": group,
        "company": company,
        "department": department,
    }
    # t2 = time.clock()
    # logger.error("getGroupDetail cost time: %f" % (t2 - t1))
    return render(request, 'sale/getGroupDetail.html', data)

@login_required()
def getSaleDetail(request):
    # t1 = time.clock()
    company = request.POST.get('company')
    department = request.POST.get('department')
    group = request.POST.get('group')
    sale = request.POST.get('sale')
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    customers = Customer.objects.filter(sales_id=sale, status=40,
                                        first_trade__lte=endDate, first_trade__gte=startDate).order_by('-first_trade')

    data = {
        "customers": customers,
        "sale": sale,
        "group": group,
        "company": company,
        "department": department,
        "startDate": str(startDate),
        "endDate": str(endDate),
    }
    # t2 = time.clock()
    # logger.error("getSaleDetail cost time: %f" % (t2 - t1))
    return render(request, 'sale/getSaleDetail.html', data)

@login_required()
def dishonestCustomerReport(request):
    #查看权限：admin ops saleboss
    # t1 =time.clock()
    if not request.user.userprofile.title.role_name in ['admin', 'ops', 'saleboss']:
        return HttpResponseRedirect("/")
    endDate = request.POST.get('endDate', "")
    if endDate == '':
        endDate = datetime.date.today()
    else:
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
    startDate = request.POST.get('startDate', "")
    if startDate == "":
        startDate = datetime.date.today() - datetime.timedelta(days=5)
    else:
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()
    companys = Sale.objects.values('company').distinct()
    if request.user.userprofile.title.role_name == 'saleboss':
        companys = companys.filter(company=request.user.userprofile.company)
    days = []
    tmpDay = startDate
    while tmpDay <= endDate:
        days.append(tmpDay)
        tmpDay = tmpDay + datetime.timedelta(days=1)
    data = {
        "startDate": str(startDate),
        "endDate": str(endDate),
        "days": days,
        "companys": companys,
    }
    # t2 = time.clock()
    # logger.error("dishonestCustomerReport cost time: %f" % (t2 - t1))
    return render(request, 'sale/dishonestCustomerReport.html', data)

@login_required()
def dishonestCustomer(request):
    # t1 =time.clock()
    if not request.user.userprofile.title.role_name in ['admin', 'ops', 'saleboss', 'salemanager', 'teacher', 'teachermanager',
                                                        'teacherboss']:
        return HttpResponseRedirect("/")
    startDate = request.GET.get('startDate','')
    endDate = request.GET.get('endDate','')
    if endDate == '':
        endDate = request.POST.get('endDate',datetime.date.today() + datetime.timedelta(days=1))
    else:
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
    if startDate == "":
        startDate = request.POST.get('startDate',datetime.date.today() - datetime.timedelta(days=0))
    else:
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()

    data = {
        "startDate": str(startDate),
        "endDate": str(endDate),
    }

    # t2 = time.clock()
    # logger.error("dishonestCustomer cost time: %f" % (t2 - t1))
    return render(request, 'sale/dishonestCustomer.html', data)

@login_required()
def queryDishonestCustomer(request):
    #查看权限：admin ops saleboss salemanager
    endDate = request.GET.get('endDate', "")
    if endDate == '':
        endDate = datetime.datetime.today() + datetime.timedelta(days=1)
    else:
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
    startDate = request.GET.get('startDate', "")
    if startDate == "":
        startDate = datetime.datetime.today()
    else:
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")

    customers = Customer.objects.filter(status=98, modify__lte=endDate, modify__gte=startDate).order_by('sales__company')
    if request.user.userprofile.title.role_name == 'saleboss':
        customers = customers.filter(sales__company=request.user.userprofile.company)
    if request.user.userprofile.title.role_name == 'salemanager':
        customers = customers.filter(sales__company=request.user.userprofile.company,
                                            sales__department=request.user.userprofile.department)
    if request.user.userprofile.title.role_name == 'teacher':
        customers = customers.filter(teacher__binduser=request.user)
    if request.user.userprofile.title.role_name == 'teachermanager':
        customers = customers.filter(teacher__company=request.user.userprofile.company, teacher__department=request.user.userprofile.department,
                                     teacher__group=request.user.userprofile.group)
    if request.user.userprofile.title.role_name == 'teacherboss':
        customers = customers.filter(teacher__company=request.user.userprofile.company)
    phone =  request.GET.get('phone', '')
    if phone :
        customers = customers.filter(phone__icontains=phone)
    wxqq = request.GET.get('wxqq', '')
    if wxqq:
        customers = customers.filter( Q(wxid__icontains=wxqq)|
                                                       Q(qqid__icontains=wxqq))
    p = Paginator(customers, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        customerPage = p.page(page)
    except (EmptyPage, InvalidPage):
        customerPage = p.page(p.num_pages)
    data = {
        # "startDate": str(startDate),
        # "endDate": str(endDate),
        # "phone": request.POST.get('phone', ''),
        # "wxqq": request.POST.get('wxqq', ''),
        "customerPage": customerPage,
        "requestArgs": getArgsExcludePage(request),
    }
    return render(request, 'sale/queryDishonestCustomer.html', data)

@login_required()
def saleKpiReportSerial(request):
    # t1 =time.clock()
    if not request.user.userprofile.title.role_name in ['admin', 'ops', 'saleboss']:
        return HttpResponseRedirect("/")
    endDate = request.POST.get('endDate', "")
    if endDate == '':
        endDate = datetime.date.today()
        # endDate = timezone.now()
    else:
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
    startDate = request.POST.get('startDate', "")
    if startDate == "":
        startDate = datetime.date.today() - datetime.timedelta(days=2)
    else:
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()
    companys = Sale.objects.values('company').distinct()
    if request.user.userprofile.title.role_name == 'saleboss':
        companys = companys.filter(company=request.user.userprofile.company)
    days = []
    tmpDay = startDate
    while tmpDay <= endDate:
        days.append(tmpDay)
        tmpDay = tmpDay + datetime.timedelta(days=1)

    data = {
        "startDate": str(startDate),
        "endDate": str(endDate),
        "days": days,
        "companys": companys,
    }
    # t2 = time.clock()
    # logger.error("saleKpiReportSerial cost time: %f" % (t2 - t1))
    return render(request, 'sale/saleKpiReportSerial.html', data)

@login_required()
def saleKpiReportForManager(request):
    # t1 = time.clock()
    if not request.user.userprofile.title.role_name in ['salemanager']:
        return HttpResponseRedirect("/")
    endDate = request.POST.get('endDate', "")
    if endDate == '':
        endDate = datetime.date.today()
    else:
        endDate = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
    startDate = request.POST.get('startDate', "")
    if startDate == "":
        startDate = datetime.date.today() - datetime.timedelta(days=30)
    else:
        startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()
    days = []
    tmpDay = startDate
    while tmpDay <= endDate:
        days.append(tmpDay)
        tmpDay = tmpDay + datetime.timedelta(days=1)
    sales = Sale.objects.filter(company=request.user.userprofile.company,
                                department=request.user.userprofile.department,
                                binduser__isnull=False)
    data = {
        "startDate": str(startDate),
        "endDate": str(endDate),
        "days": days,
        "sales": sales,
    }
    # t2 = time.clock()
    # logger.error("saleKpiReportForManager cost time: %f" % (t2 - t1))
    return render(request, 'sale/saleKpiReportForManager.html', data)