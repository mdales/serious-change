##############################################################################
##############################################################################
##
## Copyright Michael Dales (c) 2008. Made available under
## the Affero GNU Public License - see COPYING file for details.
##
##############################################################################
##############################################################################

from django.conf.urls.defaults import *
from seriouschange import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('seriouschange.signup.views',
    # Example:
    (r'^$', 'signup_page'),
    #(r'^facebook/$', 'signup_facebook'),
    # Uncomment the next line to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line for to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('', (r'^organise/', include('organise.urls')))

urlpatterns += patterns(
    '',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/pwchange/$', 'django.contrib.auth.views.password_change'),
    (r'^accounts/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^accounts/reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
)

urlpatterns += patterns('django.views',
     (r'^site_media/(?P<path>.*)$', 'static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
     (r'^media/(?P<path>.*)$', 'static.serve', 
         {'document_root': settings.ADMIN_MEDIA_ROOT}),

)

