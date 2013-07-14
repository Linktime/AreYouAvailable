from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.serializers import Serializer
from django.contrib.auth.models import User
from account.models import Account,TimeDetail

import datetime

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.select_related().all()
        resource_name = 'user'
        excludes = ['password',]
        serializer = Serializer(formats=['json',])

class AccountResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user',full=True)
    class Meta:
        queryset = Account.objects.select_related().all()
        resource_name = 'account'
        serializer = Serializer(formats=['json',])

class TimeDetailResource(ModelResource):
    accout = fields.ForeignKey(AccountResource,'user',full=True)
    class Meta:
        queryset = TimeDetail.objects.select_related().all()
        resource_name = 'timedetail'
        serializer = Serializer(formats=['json',])
    def get_object_list(self, request):
        return super(TimeDetailResource, self).get_object_list(request).filter(time=datetime.time(10,00))