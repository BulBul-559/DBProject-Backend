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

def format_datetime(dt):
        return dt.strftime("%Y/%m/%d %H:%M")
    

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
        youthol = Youtholer.objects.get(sdut_id=sdut_id)
        res = {'sdut_id': sdut_id,
               'name':youthol.name,
               'department':youthol.department,
               'identity':youthol.identity
               }
        # 在这里查询其他的信息并返回

        return HttpResponse(json.dumps(res))
    except Exception as e:
        return HttpResponse(json.dumps({'error': 'Invalid token'}))
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def StartDuty(request):
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']
    start_time =timezone.now()
    duty_state = '正常值班'

    # 这里应该请求数据库，然后判断是不是在值班时间内、是否迟到登的

    duty = DutyNow.objects.create(sdut_id=sdut_id, start_time=start_time, duty_state=duty_state)
  
    responseData = {
        'start_time': format_datetime(start_time),
        'duty_state': duty_state
    }
    return HttpResponse(json.dumps(responseData))
    # 这里应该请求数据库，然后判断是不是在值班时间内、是否迟到登的


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def FinishDuty(request):
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


    # 这里应该请求数据库，然后判断是不是在值班时间内、是否迟到登的

    return HttpResponse();



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getTodayDuty(request):
    # 正在值班+今天应该值班+今天已经结束值班
    # 这里只显示记录，所以如果一天多次反复值班，直接全部显示就行了
    # 姓名 部门 开始时间 结束时间 状态    


    # 正在值班
    duty_now_list = DutyNow.objects.all()

    # 今天应该值班

    # 今天已经结束值班

    # 姓名 部门 开始时间 结束时间 状态    
    
    responseData = []


    for item in duty_now_list:
        temp ={
            'sdut_id': item.sdut_id,
            'name': Youtholer.objects.get(sdut_id=item.sdut_id).name,
            'department': Youtholer.objects.get(sdut_id=item.sdut_id).department,
            'start_time': item.start_time.strftime("%H:%M:%S"),
            'end_time': '',
            'duty_state': item.duty_state
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
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']
    if DutyNow.objects.filter(sdut_id=sdut_id).exists():
        duty = DutyNow.objects.filter(sdut_id=sdut_id)
        responseData = {
            'start_time': format_datetime(duty[0].start_time),
            'duty_state': duty[0].duty_state
        }
        return HttpResponse(json.dumps(responseData))
    else :
        return HttpResponse(json.dumps({'duty_state': '未值班'}))
    
    return HttpResponse('未知错误')