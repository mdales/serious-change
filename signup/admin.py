##############################################################################
##############################################################################
##############################################################################
###
### seriouschange/signup/admin.py
###
### Copyright Michael Dales (c) 2008. Made available under
### the Affero GNU Public License - see COPYING file for details.
###
### Used to populate the admin interface for django
###
##############################################################################
##############################################################################
##############################################################################

from django.contrib import admin
from seriouschange.signup.models import SignupDetails, GeoData

admin.site.register(SignupDetails)
admin.site.register(GeoData)
