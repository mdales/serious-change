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

import simplejson 
import urllib

from django.db import models

from seriouschange import settings 
from seriouschange.signup.country import non_uk_countries

GOOGLE_GEOCODE_URL = "http://maps.google.com/maps/geo?key=%s&q=" % settings.GOOGLE_MAPS_API_KEY

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
    
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    class Admin:
        pass
        
    def __unicode__(self):
        return u"%s - %s" % (self.email_address, self.postcode)
        
    
    def get_location(self):
        if (self.country == 'GB'):
            address = "%s, UK" % self.postcode
        else: 
            address = None
            for x in non_uk_countries:
                if self.country == x[0]:
                    address = x[1]
            if not address:
                address = self.country
        address = urllib.quote(address)
        
        print "looking for ", address
        
        try:
            f = urllib.urlopen(GOOGLE_GEOCODE_URL + address)            
            data = simplejson.load(f)
            f.close()
        except IOError:
            # fail, so just give up
            return
        
        if data['Status']['code'] != 200:
            return
        
        placemark = data.get('Placemark', [])
        if len(placemark) == 0:
            return
            
        self.longitude = float(placemark[0]['Point']['coordinates'][0])
        self.latitude = float(placemark[0]['Point']['coordinates'][1])
        
        self.save()    
#
##############################################################################
