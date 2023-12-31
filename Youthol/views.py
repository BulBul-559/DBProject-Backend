from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth import authenticate
from django.db.models import Count

from Youthol.models import Sduter
from Youthol.models import Youtholer
from Youthol.models import DutyList
from Youthol.models import DutyNow
from Youthol.models import DutyHistory
from Youthol.models import DutyLeave
from Youthol.models import RoomBorrow

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
from intervaltree import IntervalTree


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

def judgeLocation(location):
    la_0,long_0 = location

    la_1 = 36.81255980
    long_1 = 117.9943526

    la_2 = 36.81433740
    long_2 = 117.9930294

    if la_1 <= la_0 <= la_2 and long_2 <= long_0 <= long_1:
        return True
    else:
        return False

def dutyFrameToTime(frame):
    _time = {1:"08:00", 2:"10:00", 3:"14:00", 4:"16:00", 5:"19:00" }
    return _time[frame]

def ClearYesterdayDuty():
    now_duty = DutyNow.objects.all()

    if now_duty.exists():
        for duty in now_duty:
            print(duty.sdut_id)

            DutyHistory.objects.create(sdut_id = duty.sdut_id, start_time = duty.start_time,
                                    end_time = timezone.now(), total_time = 0, extra_time = 0,
                                    duty_state = '未签退' ,duty_times = 0)
            duty.delete()
    return HttpResponse('清理完毕')

# 以下为测试接口
    
def SignUp(request):
    """
        Sign up to the system.
        Here just a simple example.
    """
    file_path = 'Youthol/sduter.xlsx'  # 请将路径替换为您的实际文件路径
    df = pd.read_excel(file_path)
    # 注册 User
    columns_to_extract = ["sdut_id","name","grade","college","department","phone","qq_number","birthday"]

    for idx, row in df[columns_to_extract].iterrows():
        username = row['sdut_id']
        password = 'youthol'
        email = f"{row['qq_number']}@qq.com"
        if User.objects.filter(username = username).exists():
            continue
        user = User.objects.create_user(username, email, password)
        user.save()

    # 注册 Sduter
    for idx, row in df[columns_to_extract].iterrows():
        sdut_id = row['sdut_id']
        name = row['name']
        college = row['college']
        grade = row['grade']
        identity = '学生'
        phone = row['phone']
        qq_number = row['qq_number']
        birthday = row['birthday']
        sduter = Sduter.objects.create(sdut_id=sdut_id, name=name, college=college, 
                                       grade=grade,identity = identity, phone=phone,
                                       qq_number=qq_number, birthday = birthday)
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

def Create(request):
    """
        Sign up to the system.
        Here just a simple example.
    """
    username = 'sunorain'
    password = 'youthol'
    email = "1079729701@qq.com"
    User.objects.create_user(username, email, password)

    sdut_id = 'sunorain'
    name = '小悠'
    college = '山东理工大学'
    grade = '214'
    identity = '学生'
    sduter = Sduter.objects.create(sdut_id=sdut_id, name=name, college=college, 
                                    grade=grade,identity = identity)
    department = '管理组'
    identity = '管理员'
    youtholer = Youtholer.objects.create(sdut_id=sdut_id, name=name, department=department, identity=identity)
    youtholer.save()

    return HttpResponse('success')

def addDuty(request):
    file_path = 'Youthol/duty.xlsx'  # 请将路径替换为您的实际文件路径
    df = pd.read_excel(file_path)
    # 注册 User
    columns_to_extract = ['sdut_id','name','day', 'frame']

    for idx, row in df[columns_to_extract].iterrows():
        sdut_id = row['sdut_id']
        day =row['day'] 
        frame=row['frame']
        if DutyList.objects.filter(sdut_id = sdut_id,day=day,frame = frame).exists():
            # 已经存在
            continue

        duty = DutyList.objects.create(sdut_id=sdut_id, day=day, frame=frame)
    return HttpResponse(status=201)

def ClearNotFinishDuty(request):
    now_duty = DutyNow.objects.all()
    if now_duty.exists():

        for duty in now_duty:
            print(duty.sdut_id)

            DutyHistory.objects.create(sdut_id = duty.sdut_id, start_time = duty.start_time,
                                    end_time = timezone.now(), total_time = 0, extra_time = 0,
                                    duty_state = '未签退' ,duty_times = 0)
            duty.delete()
    return HttpResponse('清理完毕')

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
        users = Sduter.objects.filter(sdut_id=username)

        if users.exists():
            users = users[0]

        if user is not None:
            # 生成 Refresh Token
            refresh = RefreshToken.for_user(user)

            refresh['sdut_id'] = user.username
            # 生成 Access Token
            access = refresh.access_token
            if users.first_login:
                return HttpResponse(json.dumps({'SignState':'初次登录','access_token': str(access), 'refresh_token': str(refresh)}))

            # 返回 Token 值
            return HttpResponse(json.dumps({'SignState':'登录成功','access_token': str(access), 'refresh_token': str(refresh)}))
        else:
            return HttpResponse(json.dumps({'SignState':'账号或密码错误'}))
    else:
        return HttpResponse('no params')
    
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def ChangePassword(request):
    json_param = json.loads(request.body.decode())

    username = tokenToId(request)
    password = json_param['password']
    
    user = authenticate(username=username, password=password)
    users = Sduter.objects.filter(sdut_id=username)[0]

    if user is not None:
        new_pwd = json_param['new_pwd']
        again_pwd = json_param['again_pwd']
        if(new_pwd != again_pwd):
            return HttpResponse(json.dumps({'message':'两次密码不一致'}))
        user = User.objects.get(username=username)
        user.set_password(new_pwd)
        print(new_pwd)
        user.save()

        if 'first_login' in json_param:
            users.first_login = False
            users.save()

        return HttpResponse(json.dumps({'message':'修改成功'}))
    else:
        return HttpResponse(json.dumps({'message':'原密码错误'}))

    

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
               'identity':youthol[0].identity,
               'position':youthol[0].position,
               }
        # 在这里查询其他的信息并返回

        return HttpResponse(json.dumps(res))
    except Exception as e:
        return HttpResponse(json.dumps({'error': 'Invalid token'}))

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

"""
以上为获取基本信息
以下为签到签退
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def StartDuty(request):
    """
        Start to duty
    """
    json_param = json.loads(request.body.decode())
    sdut_id = tokenToId(request)
    start_time =timezone.now()
    duty_state = '正常值班'
    latitude = json_param['latitude']
    longitude = json_param['longitude']
    # 先判断是否在位置内 
    if judgeLocation({latitude,longitude}) == False:
        return HttpResponse('不在签到范围位置内')

    # 这里应该请求数据库，然后判断是不是在值班时间内、是否迟到
    if(DutyNow.objects.filter(sdut_id=sdut_id).exists() == True):
       return HttpResponse('签到失败')
    
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
    sdut_id = tokenToId(request)
    latitude = json_param['latitude']
    longitude = json_param['longitude']
    # 先判断是否在位置内 
    if judgeLocation({latitude,longitude}) == False:
        return HttpResponse(json.dumps({'message':'不在签退范围位置内'}))


    if DutyNow.objects.filter(sdut_id = sdut_id).exists():
        duty_now = DutyNow.objects.get(sdut_id = sdut_id)
        start_time = duty_now.start_time
        end_time = timezone.now()

        # 开始判断判断状态
        total_time = (end_time - start_time).total_seconds()

        # 状态 1 时间不足
        if(total_time < 1800):
            duty_state = '值班时间不足'
            # total 和 extra 等于 0 
            DutyHistory.objects.create(sdut_id=sdut_id, start_time=start_time, 
                                       end_time=end_time, duty_state=duty_state)
            
            duty_now.delete()
            return HttpResponse(json.dumps({'message':'值班时间不足30分钟，不计入总值班时长'}));   


        # 判断是否重合，根据 sdut_id 和 day 获取到 duty_list, 然后将 frame 转换为 time 进行判断
        # 循环内处理重合，循环外处理不重合
        # 有可能一个人值班在同一天，连续值班了，所以要对结果进行累计，要对 duty_state 和 extra_time 累计

        # 初始化 
        duty_state = '正常值班'
        extra_time = total_time
        duty_times = 0
        # 获取排班
        duty_list = DutyList.objects.filter(sdut_id = sdut_id, day = (start_time.weekday() + 1))
        for _duty in duty_list:
            _frame = _duty.frame
            _time = dutyFrameToTime(_frame)

            # 获取到当前值班时间的 开始时间 和 结束时间
            _time_obj = datetime.strptime(_time, '%H:%M').time()            
            duty_start = start_time.replace(hour=_time_obj.hour, minute=_time_obj.minute, second=0, microsecond=0)
            duty_end = start_time.replace(hour=_time_obj.hour + 2, minute=_time_obj.minute, second=0, microsecond=0)

            if start_time > duty_end or end_time < duty_start:
                # 这次排班没有重合， 不表示下次没有， 所以 continue
                continue
            
            # print(start_time)
            # print(end_time)
            # print(duty_start)
            # print(duty_end)
            # 上面的 if 没有过滤掉，说明这个排班有重合
            if start_time < duty_start:
                # 开始时间早于 duty_start
                if end_time < duty_end:
                    # 结束时间早于 duty_end
                    # 判断是不是满足 90 min 
                    # 排班时间内一共 值班 end_time - duty_start 
                    in_duty_time = (end_time - duty_start).total_seconds()
                    # print(in_duty_time)
                    if in_duty_time >= 90*60:
                        # 满足 -> 正常值班 
                        # 因为要累计状态，因此这里 正常值班 才能替换
                        if duty_state == '正常值班':
                            duty_state = '正常值班'
                        extra_time -= 90*60
                        duty_times += 1
                    else:
                        # 不满足 -> 早退 
                        if duty_state == '正常值班':
                            duty_state = '早退'
                        extra_time -= in_duty_time

                else:
                    # 结束时间晚于等于 duty_end
                    # 只能是正常值班 
                    if duty_state == '正常值班':
                        duty_state = '正常值班' 
                    extra_time -= 90*60
                    duty_times += 1
            else:
                # 开始时间晚于等于 duty_start
                if end_time < duty_end:
                    # 结束时间早于 duty_end
                    # 不用额外计算了，total_time 就是
                    if total_time >= 90*60:
                        # 满足
                        if duty_state == '正常值班':
                            duty_state = '正常值班' 
                        extra_time -= 90*60
                        duty_times += 1
                    else:
                        # 不满足
                        if duty_state == '正常值班':
                            duty_state = '早退' 
                        extra_time = 0
                else:
                    # 结束时间晚于等于 duty_end
                    in_duty_time = (duty_end - start_time).total_seconds()
                    # print(in_duty_time)
                    if in_duty_time >= 90*60:
                        # 满足
                        if duty_state == '正常值班':
                            duty_state = '正常值班' 
                        extra_time -= 90*60
                        duty_times += 1                 
                    else:
                        # 不满足
                        if duty_state == '正常值班':
                            duty_state = '迟到'
                        extra_time -= in_duty_time


        # 剩下的情况都是不重合 且大于 30 min    
        # 不重合就是初始化的情况，重合则在 for 中已经处理，在这里统一存入数据库
                        
        duty_record = DutyHistory.objects.create(sdut_id = sdut_id, start_time = start_time, end_time = end_time,
                                   total_time = total_time, extra_time = extra_time,
                                   duty_state = duty_state ,duty_times = duty_times)
        duty_now.delete()
        # dic = duty_record.__dict__
        # dic.pop('_state', None)
        # print(dic)

        return HttpResponse(json.dumps({'message':'签退成功'}));   

    else:
        return HttpResponse(json.dumps({'message':'签退失败'}));


    # 这里应该请求数据库，然后判断是不是在值班时间内、是否迟到etc.


"""
以上为签到签退
以下为获取数据
"""
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GetAllYoutholer(request):
    """
        获取所有青春在线成员的信息
    """
    responseData = []
    youtholers = Youtholer.objects.all()
    for i in youtholers:
        duty = DutyList.objects.filter(sdut_id=i.sdut_id)

        duty_list = []

        for j in duty:
            day = j.day
            frame = j.frame
            duty_list.append({'day': day, 'frame': frame})

        temp = {
            'sdut_id': i.sdut_id,
            'name': i.name,
            'department' :i.department,
            'identity':i.identity,
            'duty':duty_list
        }
        responseData.append(temp)
    
    return HttpResponse(json.dumps(responseData))



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getTodayDuty(request):
    """
        Get dutied people
    """
    # 正在值班+今天已经结束值班
    # 这里只显示记录，所以如果一天多次反复值班，直接全部显示就行了
    # 姓名 部门 开始时间 结束时间 状态    
    responseData = []
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    # 正在值班
    duty_now_list = DutyNow.objects.filter(start_time__range=(today_start, today_end))
    total_duty_now = DutyNow.objects.all()
    if(duty_now_list.count() < total_duty_now.count()):
        # 所有的没结束值班的大于今天在值班的，说明昨天有人没值班，清理掉。
        ClearYesterdayDuty();
    
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


    # 今天已经结束值班

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

    return HttpResponse(json.dumps(responseData));

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getSingleDutyTime(request):
    sdut_id = tokenToId(request)
    duty = DutyList.objects.filter(sdut_id=sdut_id)

    data = []

    for i in duty:
        temp = {
            'day': i.day,
            'frame':i.frame
        }
        data.append(temp)

    while(len(data)<2):
        data.append({'day':0,'frame':0})

    return HttpResponse(json.dumps(data))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GetAllDutyRecord(request):
    """
        获取时间内全部值班记录
        一个人多条记录不会合并
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
    # contain_absence = json_param['contain_absence']
    responseData = []

    # 根据时间找需要值班的
    # 将字符串解析为日期对象
    start_date = datetime.strptime(start_time, "%Y-%m-%d")
    end_date = datetime.strptime(end_time, "%Y-%m-%d")

    """
    如果时间大于一周，则先计算完整星期内的值班次数，然后再计算不足一星期的部分
    1. 计算包含了几个完整的星期
    2. 获取全部的值班信息
    3. 根据值班信息 以及 跨越了几个完整的星期 计算出在 时间区间 内需要 值班多少次
    4. 然后遍历剩下不足一周的时间
    5. 查询每天都有谁要值班，并累计次数
    这里将需要值班的次数累计到 absence 中，随后根据请假和值班信息，剔除掉 absence 获得缺勤次数
    剔除分为两种：
    1. 请假剔除：
      + 获取到 时间范围 内的请假记录，并且剔除
      + 获取到 时间范围 内的值班记录，根据状态剔除
    """

    dutys = []

    differ_day = (end_date - start_date).days
    base_absence = int((differ_day)/7) # 跨域了几周

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
                in_youthol = Youtholer.objects.filter(sdut_id=i.sdut_id)
                if in_youthol.exists():
                    in_youthol = in_youthol[0]
                else: continue
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
    _day = [] # 筛选出 1 2 3 4 5 6 7
    w1 = start_date.weekday()
    w2 = end_date.weekday()

    # 两天相同，判断是不是同一天，否则就是超过了一周且恰好闭环
    if w1==w2:
        _day.append(w1+1)
    else:
        print("notsame day")
        for i in range(0,7):
            _day.append(w1+1)
            if(w1!=w2):
                w1 = w1+1
                w1 = w1%7
            else: break

    if(len(_day)!=0):  # 说明这几天需要筛选
        dutys = DutyList.objects.filter(day__in=_day)
        for i in dutys:
            current_sdut_id = i.sdut_id
            existing_entry = next((entry for entry in responseData if entry['sdut_id'] == current_sdut_id), None)

            if existing_entry:
                # 如果已存在相同的 sdut_id，则累加 缺勤（在下面判断是不是真的缺勤）
                existing_entry['absence'] += 1
            else:
                in_youthol = Youtholer.objects.filter(sdut_id=i.sdut_id)
                if in_youthol.exists():
                    in_youthol = in_youthol[0]
                else: continue
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

    # 上面统计的 absence 是实际上应该值班的次数
    # 经过下面过滤以后才是真正缺勤的人
    # leave 需要单独再处理  
    # 至此时间范围内所有需要值班的人以及次数已经统计完毕
    # 下面对 absence 进行剔除
    # 剔除策略是：
    # 1. 请假
    # 2. 正常值班
    start_date = start_date.replace(hour=0, minute=0, second=0)
    end_date = end_date.replace(hour=23, minute=59, second=59)
    #  使用 __range 查询获取在给定时间范围内的 请假 记录
    leave_list = DutyLeave.objects.filter(leave_date__range=(start_date,end_date))
    for i in leave_list:
        current_sdut_id = i.sdut_id
        # 找到这个人
        existing_entry = next((entry for entry in responseData if entry['sdut_id'] == current_sdut_id), None)
        
        if existing_entry:
            if existing_entry['absence'] - 1 >= 0:
                # 保证合法
                existing_entry['absence'] -= 1


    # 使用 __range 查询获取在给定时间范围内的 DutyHistory 记录
    dutys = DutyHistory.objects.filter(start_time__range=(start_date, end_date))
    print(len(dutys))
    for i in dutys:
        current_sdut_id = i.sdut_id
        existing_entry = next((entry for entry in responseData if entry['sdut_id'] == current_sdut_id), None)

        if existing_entry:
            # 这个人之前应该值班，判断一下这个值班的时间是不是在应该值班的区间
            
            existing_entry['total_time'] += i.total_time
            if existing_entry['absence'] - i.duty_times >= 0:
                # 保证合法
                existing_entry['absence'] -= i.duty_times
        else:
            # 说明这个人在时间范围内没有值班任务
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
                'total_time':i.total_time,
            }
            responseData.append(temp)
    
    return HttpResponse(json.dumps(responseData))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getSingleDutyRecord(request):
    sdut_id = tokenToId(request)

    duty = DutyHistory.objects.filter(sdut_id=sdut_id)

    data = []
    for i in duty:
        temp = {
            'start_time':formatTime(i.start_time),
            'end_time':formatTime(i.end_time),
            'total_time':i.total_time,
            'duty_state':i.duty_state,
        }
        data.append(temp)

    return HttpResponse(json.dumps(data))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getSingleLeaveRecord(request):
    sdut_id = tokenToId(request)

    leave = DutyLeave.objects.filter(sdut_id=sdut_id)

    data = []
    for i in leave:
        temp = {
            'apply_time':formatTime(i.apply_time),
            'leave_date':formatTime(i.leave_date),
            'day':i.day,
            'frame':i.frame,
        }
        data.append(temp)

    return HttpResponse(json.dumps(data))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def modifySingleYoutholInfo(request):
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']
    
    duty = json_param['duty']
    
    youthol = Youtholer.objects.filter(sdut_id=sdut_id)[0]
    youthol.department = json_param['department']
    youthol.name = json_param['name']
    youthol.identity = json_param['identity']
    youthol.save()

    duty_list = DutyList.objects.filter(sdut_id = sdut_id)
    duty_list.delete()
    for i in range(0,2):
        print(type(duty[i]['day']))
        print(duty[i]['day'])
        if(duty[i]['day']!= '0' and duty[i]['frame']!= '0'):
            DutyList.objects.create(sdut_id=sdut_id,day=duty[i]['day'],frame=duty[i]['frame'],)

    return HttpResponse('修改成功')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deletYoutholer(request):
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']

    youthol = Youtholer.objects.filter(sdut_id=sdut_id)
    if(len(youthol)!=1):
        # 有多个部门，只删除当前这个
        youthol = Youtholer.objects.filter(sdut_id=sdut_id,department=json_param['department'])
        youthol.delete()
    else:
        # 只有一个部门
        youthol.delete()
        duty = DutyHistory.objects.filter(sdut_id=sdut_id)
        duty.delete()

        duty = DutyNow.objects.filter(sdut_id=sdut_id)
        duty.delete()

        duty = DutyList.objects.filter(sdut_id=sdut_id)
        duty.delete()

        duty = DutyLeave.objects.filter(sdut_id=sdut_id);
        duty.delete()

    return HttpResponse('删除成功')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOneYoutholer(request):
    """
    1. 判断 user 中有没有
    2. 判断 sduter 中有没有
    3. 判断 youtholer 中有没有
    """
    json_param = json.loads(request.body.decode())
    sdut_id = json_param['sdut_id']

    if User.objects.filter(username=sdut_id).exists() == False:
        user = User.objects.create_user(sdut_id, f"{sdut_id}@stumail.sdut.edu.cn", 'youthol')
        user.save()

    if Sduter.objects.filter(sdut_id=sdut_id).exists() == False:
        name = json_param['name']
        college =json_param['college']
        grade = json_param['grade']
        identity = '学生'
        sduter = Sduter.objects.create(sdut_id=sdut_id, name=name, college=college, grade=grade,identity = identity)
        sduter.save()

    if Youtholer.objects.filter(sdut_id=sdut_id).exists() == False:
        sdut_id = json_param['sdut_id']
        name = json_param['name']
        department = json_param['department']
        identity = json_param['identity']
        youtholer = Youtholer.objects.create(sdut_id=sdut_id, name=name, department=department, identity=identity)
        youtholer.save()
    

    duty = json_param['duty']
    for i in range(0,2):
        if(duty[i]['day']!= 0 and duty[i]['frame']):
            DutyList.objects.create(sdut_id=sdut_id,day=duty[i]['day'],frame=duty[i]['frame'],)

    return HttpResponse('添加成功')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def applyDutyLeave(request):
    json_param = json.loads(request.body.decode())
    sdut_id = tokenToId(request)

    leave = json_param['leave']
    for str_date in leave:
        date = str_date.split(',')[0]
        day =str_date.split(',')[1]
        frame = str_date.split(',')[2]
        date_object = datetime.strptime(date, "%Y-%m-%d")
        if DutyLeave.objects.filter(sdut_id=sdut_id, leave_date=date_object,day=day,frame=frame).exists():
            return HttpResponse("重复请假")
        
    for str_date in leave:
        date = str_date.split(',')[0]
        day =str_date.split(',')[1]
        frame = str_date.split(',')[2]
        date_object = datetime.strptime(date, "%Y-%m-%d")
        DutyLeave.objects.create(sdut_id=sdut_id, apply_time=timezone.now(), leave_date=date_object,day=day,frame=frame)

    return HttpResponse("请假成功")

def toBorrowIdx(time):
    """
    给定一个形如 %H:%M 的字符串, 将其转化为借用房间时间的索引表示，
    转化规则为，以 08:00 为 0 , 08:30 为 1 , 每半小时增加 1 以此类推
    """
    time_idx = (int(time.split(':')[0])-8)*2 + int(int(time.split(':')[1])/30)
    return time_idx

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApplyRoomBorrow(request):
    json_param = json.loads(request.body.decode())
    sdut_id = tokenToId(request)
    apply_time = timezone.now()
    borrow_date = (apply_time + timedelta(days=(13-json_param['date']))).replace(hour=0,minute=0,second=0,microsecond=0)
    people = json_param['people']
    _start_time = json_param['start_time']
    _end_time = json_param['end_time']

    start_time = borrow_date.replace(hour=int(_start_time.split(':')[0]), minute=int(_start_time.split(':')[1]), second=0, microsecond=0)
    end_time  = borrow_date.replace(hour=int(_end_time .split(':')[0]), minute=int(_end_time .split(':')[1]), second=0, microsecond=0)
   
    room_id = json_param['room_id']
   
    # print(borrow_date)
    # print(start_time)

    busy_time = IntervalTree()
    busy_list = RoomBorrow.objects.filter(room_id=room_id,start_time__range=(borrow_date,borrow_date+timedelta(days=1)))
    for item in busy_list:
        start_idx = toBorrowIdx(item.start_time.strftime("%H:%M"))
        end_idx = toBorrowIdx(item.end_time.strftime("%H:%M"))
        busy_time[start_idx:end_idx] = item.id
    res = busy_time[toBorrowIdx(_start_time):toBorrowIdx(_end_time)]
    if len(res) == 0: 
        RoomBorrow.objects.create(room_id=room_id,sdut_id=sdut_id,apply_people=people, apply_time=apply_time, start_time=start_time,end_time=end_time)
        return HttpResponse("success")
    else:
        return HttpResponse("busy")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GetRoomFreeTime(request):
    return HttpResponse()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GetRoomBorrow(request):
    json_param = json.loads(request.body.decode())
    now_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = now_time + timedelta(days=14)

    resData = {}
    resData['recent14Day'] = {'dimensions':['日期'],'data':[]}
    resData['borrowTime'] = {'dimensions':['借用日期', '开始时间', '结束时间', '借用人', '开始时间', '结束时间'],'data':[]}
    for i in range(14):
        _time = now_time + timedelta(days=(13-i))
        borrow_list = RoomBorrow.objects.filter(start_time__range=(_time,(_time + timedelta(days=1))))
        str_date = _time.strftime("%m月%d日") 
        resData['recent14Day']['data'].append([str_date])
        for item in borrow_list:
            start_str1 = item.start_time.strftime("2023/07/08 %H:%M") 
            end_str1 = item.end_time.strftime("2023/07/08 %H:%M") 
            start_str2 = item.start_time.strftime("%H:%M") 
            end_str2 = item.end_time.strftime("%H:%M") 
            timeData = [i, start_str1, end_str1, item.apply_people,start_str2, end_str2]
            resData['borrowTime']['data'].append(timeData)
     
    return HttpResponse(json.dumps(resData))
    