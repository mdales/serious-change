from django.conf.urls.defaults import *
from seriouschange import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('seriouschange.signup.views',
    # Example:
    (r'^$', 'signup_page'),
    (r'^facebook/$', 'signup_facebook'),

    # Uncomment the next line to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line for to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('django.views',
     (r'^site_media/(?P<path>.*)$', 'static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
     (r'^media/(?P<path>.*)$', 'static.serve', 
         {'document_root': settings.ADMIN_MEDIA_ROOT}),

)

