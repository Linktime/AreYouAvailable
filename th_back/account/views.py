# Create your views here.

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login
from django.http import HttpResponse, HttpResponseForbidden
from tastypie.models import ApiKey
from account.models import UserGroup
import json

@csrf_exempt
def mobile_login(request):
    login_success = False
    username = request.POST['username']
    password = request.POST['password']
    response = HttpResponse()
    response['Auth_Response'] = 0
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        response['Auth_Response'] = 1
    try :
        user = authenticate(username=username,password=password)
        if not user is None:
            login(request,user)
            login_success = True
    except BaseException,e:
        print e
        response['Auth_Response'] = 2
    try:
        api_key = ApiKey.objects.get(user=user)
        response['API_Key'] = api_key.key
    except :
        pass
    return response

@csrf_exempt
def mobile_register(request):
    register_success = False
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        response = HttpResponse()
        try :
            user = User.objects.get(username=username)
            if user:
                response['register_status'] = 1
                return response
        except :
            pass
        response['register_status'] = 0
        user = User.objects.create_user(username=username,password=password)
        api_key = ApiKey.objects.get(user=user)
        response['API_Key'] = api_key.key
        return response
    else :
        return HttpResponseForbidden()

@csrf_exempt
def add_friend(request):
    if request.method == 'POST':
        auth = request.GET
        response = HttpResponse()
        data = json.loads(request.raw_post_data)
        response['register_status'] = 0
        username = auth['username']
        api_key = auth['api_key']
        try :
            user = User.objects.get(username=username)
            ApiKey.objects.get(user=user,key=api_key)
            try :
                friend = User.objects.get(username=data['friend'])
                group = UserGroup.objects.get(user=user,group_name=data['group'])
                group.member.add(friend)
                group.save()
            except User.DoesNotExist:
                response['register_status'] = 2
            except UserGroup.DoesNotExist:
                response['register_status'] = 3
        except User.DoesNotExist:
            response['register_status'] = 1
        return response
    else :
        return HttpResponseForbidden()

