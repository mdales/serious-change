
from django.conf.urls.defaults import *

# rendering for the main page
urlpatterns = patterns(
    'seriouschange.organise.views',
    (r'^$',                 'organise_overview'),
    (r'^email/$',           'email_list'),
    (r'^email/(\d+)/$',     'email_review'),
    (r'^email/compose/$',   'email_compose'),
    (r'^map/$',             'plot_users'),
)