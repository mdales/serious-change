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
class GeoData(models.Model):
    
    request_address = models.CharField(max_length=255, blank=False, null=False)
    result_address = models.CharField(max_length=255, blank=True, null=True)
    lookup_status = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    admin_area = models.CharField(max_length=255, blank=True, null=True)
    
    
    def __unicode__(self):
        return u"%s - %s, %s" % (self.request_address, self.latitude, self.longitude)
    
    def get_location_data(self, raw_address):
        address = urllib.quote(raw_address)
        
        try:
            f = urllib.urlopen(GOOGLE_GEOCODE_URL + address)            
            data = simplejson.load(f)
            f.close()
        except IOError:
            # fail, so just give up
            return
        
        self.request_address = raw_address.lower()
        self.lookup_status = int(data['Status']['code'])
        
        
        if self.lookup_status == 200:
                    
            placemark = data.get('Placemark', [])
            if len(placemark) == 0:
                return
        
            # just go by first placemark
            place = placemark[0]
        
            self.result_address = place['address']
            self.longitude = float(place['Point']['coordinates'][0])
            self.latitude = float(place['Point']['coordinates'][1])
            
            address = place['AddressDetails']
            self.country = address['Country']['CountryName']
            
            if address['Country'].has_key('AdministrativeArea'):
                self.admin_area = address['Country']['AdministrativeArea']['AdministrativeAreaName']
            
        self.save()    
#
##############################################################################


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
    
    location = models.ForeignKey(GeoData, blank=True, null=True)
    
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
        
        location, created = GeoData.objects.get_or_create(request_address=address.lower())
        
        self.location = location
        if created:
            self.location.get_location_data(address)
        self.save()
        
#
##############################################################################
