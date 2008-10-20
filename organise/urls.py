
from django.conf.urls.defaults import *

# rendering for the main page
urlpatterns = patterns(
    'organise.views',
    (r'^$',                 'organise_overview'),
    (r'^email/$',           'email_list'),
    (r'^email/compose/$',   'email_compose'),
)