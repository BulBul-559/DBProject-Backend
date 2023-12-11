from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
import json
from django.core.exceptions import ObjectDoesNotExist

# generate token and verify the token
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from datetime import timedelta




def SignUp(request):

    data = json.loads(request.body.decode())
    username = data['username']
    password = data['password']
    email = data['email']
    user = User.objects.create_user(username, email, password)
    user.save()
    return HttpResponse(status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def SignIn(request):
    json_param = json.loads(request.body.decode())
    if json_param:
    
        username = request.data.get('username')
        password = request.data.get('password')
        print(username)
        print(password)
        
        user = authenticate(username=username, password=password)

        if user is not None:
            # 生成 Refresh Token
            refresh = RefreshToken.for_user(user)
            # 过期时间 15 分钟
            # refresh.access_token.set_exp(lifetime=timedelta(minutes=15))
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
    # 只有经过身份验证的用户才能访问此视图
    # 获取用户的基本信息
    token = request.headers.get('Authorization').split(' ')[1]
    try:
        # 解析 Access Token
        access_token = AccessToken(token)
        print(access_token.payload)
        # 获取用户信息
        sdut_id = access_token.payload.get('sdut_id')

        # 在这里查询其他的信息并返回

        return HttpResponse(json.dumps({'sdut_id': sdut_id}))
    except Exception as e:
        return HttpResponse(json.dumps({'error': 'Invalid token'}))