from django.contrib import admin
from account.models import Account,TimeDetail,DateDetail,UserGroup,ShowMethod, ActivityTime, Activity

from tastypie.admin import ApiKeyInline
#from tastypie.models import ApiAccess, ApiKey
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.register(Account)
admin.site.register(TimeDetail)
admin.site.register(DateDetail)
admin.site.register(UserGroup)
admin.site.register(ShowMethod)
admin.site.register(ActivityTime)
admin.site.register(Activity)

#admin.site.register(ApiKey)
#admin.site.register(ApiAccess)

# class UserModelAdmin(UserAdmin):
#      inlines = UserAdmin.inlines + [ApiKeyInline]

# admin.site.unregister(User)
# admin.site.register(User,UserModelAdmin)