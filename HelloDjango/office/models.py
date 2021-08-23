from django.db import models
from .link_checker import Checker
# Create your models here.


class Stream(models.Model):
    baer = models.CharField(max_length=99)
    spend = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    description = models.CharField(max_length=200, blank=True)
    
    
class Site(models.Model):
    GREY = 'Не проверен'
    RED = 'Ошибка'
    YELLOW = 'Замечание'
    GREEN = 'Все ОК'

    STATUS_HTML = {
        GREY: 'status-none',
        RED: 'status-unpaid',
        YELLOW: 'status-pending',
        GREEN: 'status-paid',
    }
    CHOICE = (
        (GREY,GREY),
        (RED, RED),
        (YELLOW, YELLOW),
        (GREEN, GREEN),
    )

    site_name = models.CharField(max_length=99)
    domain = models.URLField(max_length=200)
    title = models.CharField(max_length=200)
    check_status = models.CharField(max_length=200, choices=CHOICE, default=GREY)

    def get_status_html(self):
        return self.STATUS_HTML[str(self.check_status)]

    def unpin_status(self):
        self.check_status = self.GREY

    def update_title(self):
        page = Checker(url=self.domain)
        page.make_soup()
        self.title = page.get_h1_title()

    def __str__(self):
        return self.site_name


class OldLand(models.Model):
    name = models.CharField(max_length=99)
    url = models.URLField(max_length=200)
    image = models.ImageField(upload_to='img', height_field=None, width_field=None, max_length=200)

    def __str__(self):
        return self.name


class Domain(models.Model):
    NEW = 'NEW'
    USE = 'USE'
    BAN = 'BAN'
    NEW_RU = 'Новый'
    USE_RU = 'Запускался'
    BAN_RU = 'Забанен'
    DOMAIN_STATUS = (
        (NEW, NEW_RU),
        (USE, USE_RU),
        (BAN, BAN_RU),
    )

    HTML_CLASS = {
        NEW: 'status status-paid',
        USE: 'status status-pending',
        BAN: 'status status-unpaid',
    }
    name = models.CharField(max_length=99, verbose_name='название домена', unique=True)
    url = models.URLField(max_length=300, blank=True, null=True, unique=True)
    beget_id = models.IntegerField(verbose_name='id домена на beget', unique=True)
    description = models.TextField(max_length=999, verbose_name='доп. информация', blank=True)

    # some info
    facebook = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=NEW)
    google = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=NEW)
    tiktok = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=NEW)

    def get_html_facebook(self):
        return Domain.HTML_CLASS[self.facebook]

    def get_html_google(self):
        return Domain.HTML_CLASS[self.google]

    def get_html_tiktok(self):
        return Domain.HTML_CLASS[self.tiktok]

    def __str__(self):
        return self.name


class CodeExample(models.Model):
    name = models.CharField(max_length=99, verbose_name='Пример кода')
    html_code = models.TextField(verbose_name='Html код', blank=True)
    css_code = models.TextField(verbose_name='Css код', blank=True)
    js_code = models.TextField(verbose_name='Js код', blank=True)

    def __str__(self):
        return self.name
