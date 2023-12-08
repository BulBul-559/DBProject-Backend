from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from login.models import User
import json
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

def Login(request):
    # User.objects.
    # Get the details of one question
    if(request.method == 'POST'):
        # if(request.COOKIES.get('username')):
        json_param = json.loads(request.body.decode())
        if json_param:
            try:
                user =  User.objects.get(username=json_param.get('username', ''))
            except User.DoesNotExist:
                return HttpResponse('账号不存在')
            
            if user.password == json_param.get('password', '') :
                rep = HttpResponse('登录成功');
                # rep.headers['Access-Control-Allow-Origin'] = '*'
                rep.set_cookie('username', json_param.get('username', ''))
                rep.set_cookie('is_login',1);
                return rep
            else:
                return HttpResponse('密码错误')

        else:
            return HttpResponse('no params')
    else:
        return HttpResponse("NOT POST METHOD")
    
def Logout(request):
    rep =  HttpResponse("logout")
    rep.delete_cookie('is_login')
    rep.delete_cookie('username')
    return rep