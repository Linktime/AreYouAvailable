from django.contrib import admin
from account.models import Account,TimeDetail,DateDetail,UserGroup
admin.site.register(Account)
admin.site.register(TimeDetail)
admin.site.register(DateDetail)
admin.site.register(UserGroup)