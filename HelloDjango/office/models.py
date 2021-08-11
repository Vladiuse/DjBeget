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


class Domain(models.Model):
    DEFAULT_STATUS = 'новый'
    DOMAIN_STATUS = (
        ('новый', 'новый'),
        ('запускался', 'запускался'),
        ('забанен', 'забанен'),
    )
    HTML_CLASS = {
        'новый': 'status status-paid',
        'запускался': 'status status-pending',
        'забанен': 'status status-unpaid',
    }
    name = models.CharField(max_length=99, verbose_name='название домена')
    url = models.URLField(max_length=300, blank=True, null=True)
    beget_id = models.IntegerField(verbose_name='id домена на beget')
    description = models.TextField(max_length=999, verbose_name='доп. информация', blank=True)

    # some info
    facebook = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=DEFAULT_STATUS)
    google = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=DEFAULT_STATUS)
    tiktok = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=DEFAULT_STATUS)

    def get_html_class(self, x):
        return x


