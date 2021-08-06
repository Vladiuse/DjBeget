from django.db import models

# Create your models here.


class Stream(models.Model):
    baer = models.CharField(max_length=99)
    spend = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    description = models.CharField(max_length=200, blank=True)
    
    
class Site(models.Model):
    site_name = models.CharField(max_length=99)
    domain = models.URLField(max_length=200)
    title = models.CharField(max_length=200)


class OldLand(models.Model):
    name = models.CharField(max_length=99)
    url = models.URLField(max_length=200)
    image = models.ImageField(upload_to='img', height_field=None, width_field=None, max_length=200)

