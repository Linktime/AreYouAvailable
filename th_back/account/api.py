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
from account.tools import TimeData, get_userGroup_freeTime_Data, get_Somebody_freeTime_Data, timeToPerson, reGroupByWeek

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
        #return bundle.obj.user == bundle.request.user
        return True

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


# TODO
class OnlyReadByUsetoAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        group = UserGroup.objects.filter(member=bundle.request.user)
        #object_list.filter
        return object_list.filter(useto=bundle.request.user)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        #bundle.obj
        return True
        #return bundle.obj.user == bundle.request.user

    def create_list(self, object_list, bundle):
        # Assuming their auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        #return bundle.obj.user == bundle.request.user
        return True

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


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.select_related().all()
        resource_name = 'user'
        excludes = ['password','is_active','is_staff','is_superuser','first_name','last_name']
        allowed_method = ['get','put',]
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        #authorization = UserObjectsOnlyAuthorization()
        #authorization = DjangoAuthorization()
        filtering = {
            'username':ALL,
        }

class SimpleUserResource(ModelResource):
    class Meta:
        queryset = User.objects.select_related().all()
        resource_name = 'simpleuser'
        fields = ['username']
        filtering = {
            'username':ALL
        }
        authentication = ApiKeyAuthentication()
        allowed_method = ['get']
        serializer = Serializer(formats=['json',])  

    # def obj_create(self,bundle,**kwargs):  
    #     friend = bundle.data['friend']
    #     # group = bundle.data['group']
    #     user = bundle.request.user
    #     print friend
    #     return bundle

class AccountResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user',full=True)
    class Meta:
        queryset = Account.objects.select_related('user').all()
        resource_name = 'account'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()

class UserGroupResource(ModelResource):
    member = fields.ManyToManyField(UserResource,'member',full=True)
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

class TimeDetailResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    useto = fields.ToManyField(UserResource, 'useto',null=True,full=True)
    useto_group = fields.ToManyField(UserGroupResource, 'useto_group',null=True)
    class Meta:
        queryset = TimeDetail.objects.select_related().all()
        resource_name = 'timedetail'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
    def obj_create(self, bundle, **kwargs):
        bundle.data['user'] = bundle.request.user
        start_time = bundle.data['start_time'].strip().split(':')
        end_time = bundle.data['end_time'].strip().split(':')
        bundle.data['start_time'] = datetime.time(int(start_time[0]),int(start_time[1]))
        bundle.data['end_time'] = datetime.time(int(end_time[0]),int(end_time[1]))
        bundle =  super(TimeDetailResource,self).obj_create(bundle)
        # TODO 
        # Add group
        return bundle

    # def get_object_list(self, request):
    #     account = Account.objects.get(request.user)
    #     return super(TimeDetailResource, self).get_object_list(request).filter(user=account)

class SimpleTimeDetailResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = TimeDetail.objects.select_related().all()
        resource_name = 'simpletimedetail'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = OnlyReadByUsetoAuthorization()

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

class FreeTimeListSingleResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = Account.objects.select_related('user').all()
        resource_name = 'freetimelist/single'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
        allowed_method = ['get',]
    def dehydrate(self, bundle):
        try :
            person = User.objects.get(username=bundle.request.GET['person'])
        except :
            bundle.data['freelist'] = None
            return bundle
        freelist = get_Somebody_freeTime_Data(bundle.request.user,[person,])
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

class TimeToPersonResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')
    class Meta:
        queryset = Account.objects.select_related('user').all()
        resource_name = 'freetimelist/timetoperson'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
        allowed_method = ['get',]
    def dehydrate(self, bundle):
        #
        user = bundle.request.user
        times = bundle.request.GET['time'].split('~')
        # FIXME
        # try :
        #     weekday = bundle.request.GET['weekday']
        # except:
        weekday = None
        start_times = times[0].strip().split(':')
        start_time = datetime.time(int(start_times[0]),int(start_times[1]))
        end_times = times[1].strip().split(':')
        end_time = datetime.time(int(end_times[0]),int(end_times[1]))
        timedata = TimeData(start_time,end_time,[user,])
        freelist = timeToPerson(timedata,weekday)
        freelist_data=[]
        if not weekday:
            freelist = reGroupByWeek(freelist)
            i = 0
            for weekday in freelist:
                i += 1
                userlist = map(lambda x:x.user,weekday)
                freelist_day = ({'count':len(weekday),'userlist':userlist,'time':weekday})
                freelist_data.append({'weekday':i,'freelist_time':freelist_day})
        else :
            userlist = map(lambda x:x.user,freelist)
            freelist_day = ({'count':len(freelist),'userlist':userlist,'time':freelist})
            freelist_data.append({'weekday':weekday,'freelist_time':freelist_day})
        bundle.data['freelist'] = freelist_data
        return bundle


post_save.connect(create_api_key, sender=User)