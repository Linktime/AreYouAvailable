# -*- coding:utf-8 -*-
from tastypie.resources import ModelResource,ALL_WITH_RELATIONS,ALL
from tastypie import fields
from tastypie.serializers import Serializer
from django.contrib.auth.models import User
from account.models import Account,TimeDetail,DateDetail,UserGroup,Activity,ActivityTime, ActivityNotify
from django.db.models.signals import post_save
from tastypie.models import create_api_key
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization,DjangoAuthorization
from account.tools import get_userGroup_freeTime_Data

import datetime
import sys

from django.dispatch import Signal

Activity_create_signal = Signal(providing_args=['activity_sender','member','activiyt'])


class UserObjectsOnlyAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        return bundle.obj.user == bundle.request.user

    def create_list(self, object_list, bundle):
        # Assuming their auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        #raise Unauthorized("Sorry, no deletes.")
        return object_list.filter(user=bundle.request.user)

    def delete_detail(self, object_list, bundle):
        #raise Unauthorized("Sorry, no deletes.")
        return bundle.obj.user == bundle.request.user

class NotifyAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        return object_list.filter(sender=bundle.request.user)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        return bundle.obj.sender == bundle.request.user

    def create_list(self, object_list, bundle):
        # Assuming their auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        print '-----------------',bundle.obj.__dict__
        #return bundle.obj.sender == bundle.request.user
        return True


    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.sender == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.sender == bundle.request.user or bundle.obj.member == bundle.request.user

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        #raise Unauthorized("Sorry, no deletes.")
        return object_list.filter(sender=bundle.request.user)

    def delete_detail(self, object_list, bundle):
        #raise Unauthorized("Sorry, no deletes.")
        return bundle.obj.sender == bundle.request.user


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.select_related().all()
        resource_name = 'user'
        excludes = ['password','is_active','is_staff','is_superuser']
        allowed_method = ['get','put',]
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        #authorization = UserObjectsOnlyAuthorization()
        #authorization = DjangoAuthorization()
        filtering = {
            'username':ALL,
        }
        #always_return_data = True

class AccountResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = Account.objects.select_related('user').all()
        resource_name = 'account'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()

class TimeDetailResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = TimeDetail.objects.select_related().all()
        resource_name = 'timedetail'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
    def obj_create(self, bundle, **kwargs):
        bundle.data['user'] = bundle.request.user
        return super(TimeDetailResource,self).obj_create(bundle)

    # def get_object_list(self, request):
    #     account = Account.objects.get(request.user)
    #     return super(TimeDetailResource, self).get_object_list(request).filter(user=account)

class DateDetailResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = DateDetail.objects.select_related().all()
        resource_name = 'datedetail'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
    def obj_create(self, bundle, **kwargs):
        bundle.data['user'] = bundle.request.user
        return super(TimeDetailResource,self).obj_create(bundle)

# class ShowMethodResource(ModelResource):
#     user = fields.ForeignKey(UserResource,'user')
#     class Meta:
#         queryset = ShowMethod.objects.select_related().all()
#         resource_name = 'showmethod'
#         serializer = Serializer(formats=['json',])
#         authentication = ApiKeyAuthentication()
#         authorization = UserObjectsOnlyAuthorization()
#     def obj_create(self, bundle, **kwargs):
#         bundle.data['user'] = bundle.request.user
#         return super(TimeDetailResource,self).obj_create(bundle)

class UserGroupResource(ModelResource):
    member = fields.ManyToManyField(UserResource,'member')
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = UserGroup.objects.select_related().all()
        resource_name = 'usergroup'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
    def obj_create(self, bundle, **kwargs):
        bundle.data['user'] = bundle.request.user
        return super(TimeDetailResource,self).obj_create(bundle)

class ActivityResource(ModelResource):
    participant = fields.ToManyField(UserResource,'participant',null=True)
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = Activity.objects.select_related().all()
        resource_name = 'activity'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
    def obj_create(self, bundle, **kwargs):
        bundle.data['user'] = bundle.request.user
        #Activity_create_signal.send(sender=self.__class__,activity_sender=bundle.request.user,member=bundle.data['participant'])        
        bundle.data['participant'] = None
        return super(ActivityResource,self).obj_create(bundle)

class ActivityTimeResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = ActivityTime.objects.select_related().all()
        resource_name = 'activitytime'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
    def obj_create(self, bundle, **kwargs):
        bundle.data['user'] = bundle.request.user
        return super(TimeDetailResource,self).obj_create(bundle)

class ActivityNotifyResource(ModelResource):
    sender = fields.ForeignKey(UserResource,'sender')
    member = fields.ToManyField(UserResource,'member')
    activity = fields.ForeignKey(ActivityResource,'activity')
    class Meta:
        queryset = ActivityNotify.objects.select_related().all()
        resource_name = "activitynotify"
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = NotifyAuthorization()
        allowed_method = ['post','put',]


class FreeTimeListResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = Account.objects.select_related('user').all()
        resource_name = 'freetimelist/group'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
        allowed_method = ['get',]
    def dehydrate(self, bundle):
        # Include the request IP in the bundle.
        freelist = get_userGroup_freeTime_Data(bundle.request.user,bundle.request.GET['group_name'])
        freelist_data=[]
        i=0
        for weekday in freelist:
            i += 1
            freelist_day = []
            for timedetail in weekday:
                count = timedetail.count
                userlist = timedetail.userlist
                freelist_day.append({'count':count,'userlist':userlist,'time':timedetail})
            freelist_data.append({'weekday':i,'freelist_time':freelist_day})
        bundle.data['freelist'] = freelist_data
        return bundle

post_save.connect(create_api_key, sender=User)