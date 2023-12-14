from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth import authenticate


from Youthol.models import Sduter
from Youthol.models import Youtholer
from Youthol.models import DutyList
from Youthol.models import DutyNow
from Youthol.models import DutyHistory


# generate token and verify the token
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

import pandas as pd
import random
import json

def formatTime(dt):
        return dt.strftime("%Y/%m/%d %H:%M")

def tokenToId(request):
    token = request.headers.get('Authorization').split(' ')[1]
    try:
        # 解析 Access Token
        access_token = AccessToken(token)
        return  access_token.payload.get('sdut_id')
    except Exception as e:
        return HttpResponse(json.dumps({'error': 'Invalid token'}))

    

def SignUp(request):
    """
        Sign up to the system.
        Here just a simple example.
    """
    file_path = 'Youthol/sduter.xlsx'  # 请将路径替换为您的实际文件路径
    df = pd.read_excel(file_path)
    # 注册 User
    columns_to_extract = ['sdut_id','name','department', 'grade', 'phone']

    for idx, row in df[columns_to_extract].iterrows():
        username = row['sdut_id']
        password = 'youthol'
        email = f"{row['sdut_id']}@stumail.sdut.edu.cn"
        if User.objects.filter(username = username).exists():
            continue
        user = User.objects.create_user(username, email, password)
        user.save()
    # 注册 Sduter
    for idx, row in df[columns_to_extract].iterrows():
        sdut_id = row['sdut_id']
        name = row['name']
        college = '山东理工大学'
        class_number = row['grade']
        identity = '学生'
        sduter = Sduter.objects.create(sdut_id=sdut_id, name=name, college=college, class_number=class_number,identity = identity)
        sduter.save()
    # 注册 Youther
    for idx, row in df[columns_to_extract].iterrows():
        sdut_id = row['sdut_id']
        name = row['name']
        department = row['department']
        identity = '试用'
        youtholer = Youtholer.objects.create(sdut_id=sdut_id, name=name, department=department, identity=identity)
        youtholer.save()

    # data = json.loads(request.body.decode())
    # username = data['username']
    # password = data['password']
    # email = data['email']
    # user = User.objects.create_user(username, email, password)
    # user.save()
    return HttpResponse(status=201)


def addDuty(request):
    file_path = 'Youthol/sduter.xlsx'  # 请将路径替换为您的实际文件路径
    df = pd.read_excel(file_path)
    # 注册 User
    columns_to_extract = ['sdut_id','name','department', 'grade', 'phone']

    for idx, row in df[columns_to_extract].iterrows():
        username = row['sdut_id']
        day =random.randint(1, 7)
        frame=random.randint(1, 5)
        duty = DutyList.objects.create(sdut_id=username, day=day, frame=frame)
    return HttpResponse(status=201)

# 以上为测试接口

@api_view(['POST'])
@permission_classes([AllowAny])
def SignIn(request):
    """
        Sign in the system
    """
    json_param = json.loads(request.body.decode())
    if json_param:
        username = json_param['username']
        password = json_param['password']
        
        user = authenticate(username=username, password=password)

        if user is not None:
            # 生成 Refresh Token
            refresh = RefreshToken.for_user(user)
            # 过期时间 15 分钟
            # refresh.access_token.set_exp(lifetime=timedelta(days=15))
            refresh['sdut_id'] = user.username
            # 生成 Access Token
            access = refresh.access_token

            # 返回 Token 值
            return HttpResponse(json.dumps({'SignState':'登录成功','access_token': str(access), 'refresh_token': str(refresh)}))
        else:
            return HttpResponse(json.dumps({'SignState':'账号或密码错误'}))
    else:
        return HttpResponse('no params')


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def GetUserInfo(request):
    """
        Verify the token and return the user basic infomation.
        1. sdut_id (same as username)

    """
    # 只有经过身份验证的用户才能访问此视图
    # 获取用户的基本信息
    token = request.headers.get('Authorization').split(' ')[1]
    try:
        # 解析 Access Token
        access_token = AccessToken(token)
        # 获取用户信息
        sdut_id = access_token.payload.get('sdut_id')

        # 在这里查询其他的信息并返回

        return HttpResponse(json.dumps({'sdut_id': sdut_id}))
    except Exception as e:
        return HttpResponse(json.dumps({'error': 'Invalid token'}))
    


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def getYoutholerInfo(request):
    """
        Verify the token and return the user basic infomation.
        1. sdut_id (same as username)

    """
    # 只有经过身份验证的用户才能访问此视图
    # 获取用户的基本信息
    token = request.headers.get('Authorization').split(' ')[1]
    try:
        # 解析 Access Token
        access_token = AccessToken(token)
        # 获取用户信息
        sdut_id = access_token.payload.get('sdut_id')
        youthol = Youtholer.objects.filter(sdut_id=sdut_id)
        res = {'sdut_id': sdut_id,
               'name':youthol[0].name,
               'department':youthol[0].department,
               'identity':youthol[0].identity
               }
        # 在这里查询其他的信息并返回

        return HttpResponse(json.dumps(res))
    except Exception as e:
        return HttpResponse(json.dumps({'error': 'Invalid token'}))
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def StartDuty(request):
    """
        Start to duty
    """
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']
    start_time =timezone.now()
    duty_state = '正常值班'

    # 这里应该请求数据库，然后判断是不是在值班时间内、是否迟到登的

    duty = DutyNow.objects.create(sdut_id=sdut_id, start_time=start_time, duty_state=duty_state)
  
    responseData = {
        'start_time': formatTime(start_time),
        'duty_state': duty_state
    }
    return HttpResponse(json.dumps(responseData))
    # 这里应该请求数据库，然后判断是不是在值班时间内、是否迟到登的


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def FinishDuty(request):
    """
        Finish the Duty
    """
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']

    message = '签退成功'

    if DutyNow.objects.filter(sdut_id = sdut_id).exists():
        duty_now = DutyNow.objects.get(sdut_id = sdut_id)
        start_time = duty_now.start_time
        end_time = timezone.now()
        total_time = (end_time - start_time).total_seconds()

        if(total_time<1800):
            duty_state = '值班时间不足30分钟'

            duty_recode = DutyHistory.objects.create(sdut_id=sdut_id, start_time=start_time, 
                                                     end_time=end_time, total_time = total_time,
                                                     duty_state=duty_state)
            
            message = '值班时间不足30分钟，不计入总值班时长';
        else:
            duty_state = '正常值班'
            duty_recode = DutyHistory.objects.create(sdut_id=sdut_id, start_time=start_time, 
                                            end_time=end_time, total_time = total_time,
                                            duty_state=duty_state)
        duty_now.delete()
        return HttpResponse(json.dumps({'message':message}));   
    else:
        return HttpResponse(json.dumps({'message':'签退失败'}));


    # 这里应该请求数据库，然后判断是不是在值班时间内、是否迟到etc.


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getTodayDuty(request):
    """
        Get dutied people
    """
    # 正在值班+今天应该值班+今天已经结束值班
    # 这里只显示记录，所以如果一天多次反复值班，直接全部显示就行了
    # 姓名 部门 开始时间 结束时间 状态    
    responseData = []

    # 正在值班
    duty_now_list = DutyNow.objects.all()
    
    # 姓名 部门 开始时间 结束时间 状态    
    for item in duty_now_list:
        temp ={
            'sdut_id': item.sdut_id,
            'name': Youtholer.objects.filter(sdut_id=item.sdut_id)[0].name,
            'department': Youtholer.objects.filter(sdut_id=item.sdut_id)[0].department,
            'start_time': item.start_time.strftime("%H:%M:%S"),
            'end_time': '',
            'duty_state': '正在值班',
            'total_time': (timezone.now() - item.start_time).total_seconds()
        }
        responseData.append(temp)

    # 今天应该值班

    # 今天已经结束值班
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    today_duty_history = DutyHistory.objects.filter(start_time__range=(today_start, today_end))
    
    # 姓名 部门 开始时间 结束时间 状态    
    for item in today_duty_history:
        temp ={
            'sdut_id': item.sdut_id,
            'name': Youtholer.objects.filter(sdut_id=item.sdut_id)[0].name,
            'department': Youtholer.objects.filter(sdut_id=item.sdut_id)[0].department,
            'start_time': item.start_time.strftime("%H:%M:%S"),
            'end_time': item.end_time.strftime("%H:%M:%S"),
            'duty_state': item.duty_state,
            'total_time': item.total_time
        }
        responseData.append(temp)

    # for i in res:
    #     comments = Comments.objects.filter(quesId=i.id).count()
    #     temp = {
    #         'id': i.id,
    #         'ques': i.ques,
    #         'commentsNum': comments
    #     }
    #     responseData.append(temp)

    return HttpResponse(json.dumps(responseData));

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def CheckDuty(request):
    """
        配合前端生命周期函数，检查是否正在值班
    """

    sdut_id = tokenToId(request)

    if DutyNow.objects.filter(sdut_id=sdut_id).exists():
        duty = DutyNow.objects.filter(sdut_id=sdut_id)
        responseData = {
            'start_time': formatTime(duty[0].start_time),
            'duty_state': duty[0].duty_state
        }
        return HttpResponse(json.dumps(responseData))
    else :
        return HttpResponse(json.dumps({'duty_state': '未值班'}))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GetAllYoutholer(request):
    """
        获取所有青春在线成员的信息
    """
    responseData = []
    youtholers = Youtholer.objects.all()
    for i in youtholers:
        temp = {
            'sdut_id': i.sdut_id,
            'name': i.name,
            'department' :i.department,
            'identity':i.identity
        }
        responseData.append(temp)
    
    return HttpResponse(json.dumps(responseData))



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GetAllDuty(request):
    """
        获取时间内全部值班记录
        一个人多条记录将会分开返回
    """

    responseData = []
    dutys = DutyHistory.objects.all()
    for i in dutys:
        temp = {
            'sdut_id': i.sdut_id,
            'name': Youtholer.objects.filter(sdut_id=i.sdut_id)[0].name,
            'department': Youtholer.objects.filter(sdut_id=i.sdut_id)[0].department,
            'start_time':formatTime(i.start_time),
            'end_time':formatTime(i.end_time),
            'total_time':i.total_time,
            'duty_state':i.duty_state,
        }
        responseData.append(temp)
    
    return HttpResponse(json.dumps(responseData))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GetTotalDutyInRange(request):
    """
        获取时间范围内所有值班信息(总时长)
    """
    # 1. 所有应该值班的人
    # 2. 所有值过班的人
    #  先把时间内应该值班的人筛选出来
    #  然后再用 DutyHistory 合并

    json_param = json.loads(request.body.decode())
    start_time = json_param['start_time']
    end_time = json_param['end_time']
    responseData = []

    # 根据时间找需要值班的
    # 将字符串解析为日期对象
    start_date = datetime.strptime(start_time, "%Y-%m-%d")
    end_date = datetime.strptime(end_time, "%Y-%m-%d")

    dutys = []

    differ_day = (end_date - start_date).days
    base_absence = int((differ_day)/7) # 跨域了几周
    print(base_absence)
    print(differ_day)
    
    # 如果时间大于一周，则会直接获取全部，然后再单独处理剩下多余的
    if differ_day >= 7:
        print("more than 7 days")
        dutys = DutyList.objects.all()
        for i in dutys:
            current_sdut_id = i.sdut_id
            existing_entry = next((entry for entry in responseData if entry['sdut_id'] == current_sdut_id), None)

            if existing_entry:
                # 如果已存在相同的 sdut_id，则累加 缺勤（在下面判断是不是真的缺勤）
                existing_entry['absence'] += 1
            else:
                in_youthol = Youtholer.objects.filter(sdut_id=i.sdut_id)[0]
                temp = {
                    'sdut_id': i.sdut_id,
                    'name': in_youthol.name,
                    'department': in_youthol.department,
                    'identity': in_youthol.identity,
                    'total_time':0,
                    'absence':base_absence,
                    'leave':0
                    # 'duty_state':i.duty_state,
                }
                responseData.append(temp)

    # 处理多余的部分
    _day = []
    w1 = start_date.weekday()
    w2 = end_date.weekday()

    # 两天相同，判断是不是同一天，否则就是超过了一周且恰好闭环
    if w1==w2:
        print("same day")
        _day.append(w1+1)
    else:
        print("notsame day")
        for i in range(0,7):
            _day.append(w1+1)
            if(w1!=w2):
                w1 = w1+1
                w1 = w1%7
            else: break
    print(_day)

    if(len(_day)!=0):
        dutys = DutyList.objects.filter(day__in=_day)
        print(len(dutys))
        for i in dutys:
            current_sdut_id = i.sdut_id
            existing_entry = next((entry for entry in responseData if entry['sdut_id'] == current_sdut_id), None)

            if existing_entry:
                # 如果已存在相同的 sdut_id，则累加 缺勤（在下面判断是不是真的缺勤）
                existing_entry['absence'] += 1
            else:
                in_youthol = Youtholer.objects.filter(sdut_id=i.sdut_id)[0]
                temp = {
                    'sdut_id': i.sdut_id,
                    'name': in_youthol.name,
                    'department': in_youthol.department,
                    'identity': in_youthol.identity,
                    'total_time':0,
                    'absence':1 + base_absence,
                    'leave':0
                    # 'duty_state':i.duty_state,
                }
                responseData.append(temp)

        # 上面统计的 absence 是实际上应该值班的次数，经过下面过滤以后才是真正缺勤的人
        # leave 需要单独再处理

    dutys = DutyHistory.objects.all()
    for i in dutys:
        current_sdut_id = i.sdut_id
        existing_entry = next((entry for entry in responseData if entry['sdut_id'] == current_sdut_id), None)

        if existing_entry:
            # 这个人之前应该值班，判断一下这个值班的时间是不是在应该值班的区间

            existing_entry['total_time'] += i.total_time
        else:
            # 说明这个人之前没有值班任务
            in_youthol = Youtholer.objects.filter(sdut_id=i.sdut_id)[0]
            temp = {
                'sdut_id': i.sdut_id,
                'name': in_youthol.name,
                'department': in_youthol.department,
                'identity': in_youthol.identity,
                'total_time':i.total_time,
                'absence':0,
                'leave':0
                # 'duty_state':i.duty_state,
            }
            responseData.append(temp)
    
    return HttpResponse(json.dumps(responseData))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GetSingleTotalDuty(request):
    """
        获取一个人值班总时长
    """
    sdut_id = tokenToId(request)
    responseData = []
    dutys = DutyHistory.objects.filter(sdut_id=sdut_id)
    for i in dutys:
        current_sdut_id = i.sdut_id
        existing_entry = next((entry for entry in responseData if entry['sdut_id'] == current_sdut_id), None)

        if existing_entry:
            # 如果已存在相同的 sdut_id，则累加 total_time
            existing_entry['total_time'] += i.total_time
        else:
            temp = {
                'sdut_id': i.sdut_id,
                'name': Youtholer.objects.filter(sdut_id=i.sdut_id)[0].name,
                'department': Youtholer.objects.filter(sdut_id=i.sdut_id)[0].department,
                'start_time':formatTime(i.start_time),
                'end_time':formatTime(i.end_time),
                'total_time':i.total_time,
                'duty_state':i.duty_state,
            }
            responseData.append(temp)
    
    return HttpResponse(json.dumps(responseData))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def modifySingleYoutholInfo(request):
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']

    youthol = Youtholer.objects.filter(sdut_id=sdut_id)[0]

    youthol.department = json_param['department']
    youthol.name = json_param['name']
    youthol.identity = json_param['identity']
    youthol.save()

    return HttpResponse('修改成功')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deletYoutholer(request):
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']

    youthol = Youtholer.objects.filter(sdut_id=sdut_id)[0]
    
    youthol.delete()
    return HttpResponse('删除成功')