from django.conf.urls import patterns, include, url
from views import home
from tastypie.api import Api
from account.api import AccountResource,TimeDetailResource,UserResource,DateDetailResource,UserGroupResource,ShowMethodResource,FreeTimeListResource
from account.api import ActivityResource, ActivityTimeResource

api = Api(api_name='data')
api.register(AccountResource())
api.register(TimeDetailResource())
#api.register(UserResource())
api.register(UserGroupResource())
api.register(DateDetailResource())
api.register(ShowMethodResource())
api.register(ActivityResource())
api.register(ActivityTimeResource())
api.register(FreeTimeListResource())

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$',home),
	url(r'^account/',include('account.urls')),
	url(r'^api/',include(api.urls)),
    url(r'^login/$','account.views.mobile_login'),
    url(r'^register/$','account.views.mobile_register'),
    # Examples:
    # url(r'^$', 'th_back.views.home', name='home'),
    # url(r'^th_back/', include('th_back.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
