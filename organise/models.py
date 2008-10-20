from django.db import models

# Create your models here.


class MailEvent(models.Model):
    
    from_address = models.EmailField(default='hello@seriouschange.org.uk')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    date_sent = models.DateTimeField()
    
    def __unicode__(self):
        return self.subject