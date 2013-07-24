# Create your views here.

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login
from django.http import HttpResponse
from tastypie.models import ApiKey

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
    except :
        response['Auth_Response'] = 2
    try:
        api_key = ApiKey.objects.get(user=user)
        response['API_Key'] = api_key.key
    except :
        pass
    return response


