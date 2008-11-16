##############################################################################
##############################################################################
##############################################################################
###
### seriouschange/signup/models.py
###
### Copyright Michael Dales (c) 2008. Made available under
### the Affero GNU Public License - see COPYING file for details.
###
##############################################################################
##############################################################################

###
##############################################################################
##############################################################################
##############################################################################


from django.db import models

##############################################################################
#
class SignupDetails(models.Model):
    email_address = models.EmailField(blank=False, null=False)
    postcode = models.CharField(max_length=8, blank=True)
    version_string = models.CharField(max_length=255)
    creation_time = models.DateTimeField(blank=False, null=False)
    creation_ipaddr = models.CharField(max_length=15, blank=False, null=False)
    country = models.CharField(max_length=128, blank=False, null=False, 
        default='GB')
    
    class Admin:
        pass
        
    def __unicode__(self):
        return u"%s - %s" % (self.email_address, self.postcode)
#
##############################################################################
