from tastypie.resources import ModelResource,ALL_WITH_RELATIONS,ALL
from tastypie import fields
from tastypie.serializers import Serializer
from django.contrib.auth.models import User
from account.models import Account,TimeDetail,DateDetail,ShowMethod,UserGroup
from django.db.models.signals import post_save
from tastypie.models import create_api_key
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization,DjangoAuthorization


import datetime


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
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.select_related().all()
        resource_name = 'user'
        excludes = ['password','is_active','is_staff','is_superuser']
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        #authorization = UserObjectsOnlyAuthorization()
        authorization = DjangoAuthorization()
        filtering = {
            'username':ALL,
        }
        #always_return_data = True

class AccountResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user',full=True)
    class Meta:
        queryset = Account.objects.select_related().all()
        resource_name = 'account'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()

class TimeDetailResource(ModelResource):
    accout = fields.ForeignKey(AccountResource,'user',full=True)
    class Meta:
        queryset = TimeDetail.objects.select_related().all()
        resource_name = 'timedetail'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()
    # def get_object_list(self, request):
    #     return super(TimeDetailResource, self).get_object_list(request).filter(time=datetime.time(10,00))

class DateDetailResource(ModelResource):
    accout = fields.ForeignKey(AccountResource,'user',full=True)
    class Meta:
        queryset = DateDetail.objects.select_related().all()
        resource_name = 'datedetail'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()

class ShowMethodResource(ModelResource):
    accout = fields.ForeignKey(AccountResource,'user',full=True)
    class Meta:
        queryset = ShowMethod.objects.select_related().all()
        resource_name = 'showmethod'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()

class UserGroupResource(ModelResource):
    accout = fields.ForeignKey(AccountResource,'user',full=True)
    class Meta:
        queryset = UserGroup.objects.select_related().all()
        resource_name = 'usergroup'
        serializer = Serializer(formats=['json',])
        authentication = ApiKeyAuthentication()
        authorization = UserObjectsOnlyAuthorization()

post_save.connect(create_api_key, sender=User)