from django.db import models
# develop?
# Create your models here.
from .api import MyError
from .link_checker import Checker


class Stream(models.Model):
    # TODO удалить
    baer = models.CharField(max_length=99)
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.CharField(max_length=200, blank=True)


class Site(models.Model):
    """
    Сайт
    """
    NOT_TITLE = ['None', MyError.NO_CONNECTION, '404 Not Found']

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
        (GREY, GREY),
        (RED, RED),
        (YELLOW, YELLOW),
        (GREEN, GREEN),
    )

    site_name = models.CharField(max_length=99)
    domain = models.URLField(max_length=200, verbose_name='Ссылка сайта')
    title = models.CharField(max_length=200, verbose_name='Заголовок сайта')
    check_status = models.CharField(max_length=200, choices=CHOICE, default=GREY, verbose_name='Статус проверки сайта')

    def get_http_site(self):
        return f'http://{self.site_name}/'

    def get_https_site(self):
        return f'https://{self.site_name}/'

    def get_status_html(self):
        return self.STATUS_HTML[str(self.check_status)]

    def unpin_status(self):
        """Установить дефолтный статус"""
        self.check_status = self.GREY

    def set_status(self, status):
        """Статус сайта от чекера"""
        for k, v in self.STATUS_HTML.items():
            if status == v:
                self.check_status = k
                break
        self.save()
        #
        # dic = {
        #     self.GREY:'Не проверен',
        #     self.RED:'Ошибка',
        #     self.YELLOW:'Замечание',
        #     self.GREEN:'Все ОК',
        # }
        # self.check_status = dic[status]

    def update_title(self, hard=None):
        """Обновить залоговок сайта - title"""
        if not hard:
            if self.title not in self.NOT_TITLE:
                return
        url = self.get_http_site()
        page = Checker(url=url)
        try:
            page.make_soup()
        except MyError:
            self.title = MyError.NO_CONNECTION
        else:
            self.title = page.get_h1_title()

    def get_log_url(self):
        """Ссылка на лог сайта"""
        return str(self.domain) + 'log.txt'

    def get_beget_editor(self):
        """Ссылка на редактор сайта в web-beget"""
        site = self.site_name
        if 'vladiuse' in site:
            site = 'old-lands'
        site += '/public_html'
        return f'https://cp.beget.com/fm/%7B%22type%22:%22home%22,%22path%22:%22/{site}%22%7D'

    @staticmethod
    def get_sort_name(site_model):
        site_name = site_model.site_name
        if site_name.count('.') == 1:
            return site_name + 'aaa'
        sub = site_name[:site_name.find('.')]
        dom = site_name[site_name.find('.') + 1:]
        return dom + sub

    def status_sub(self):
        sub_domain_class = 'sub-dom'
        domain_class = 'dom'
        if self.site_name.count('.') == 2 and 'beget' not in self.site_name:
            return sub_domain_class
        return domain_class


    def __str__(self):
        return self.site_name


class OldLand(models.Model):
    # TODO обьеденить с моделью Site?
    """
    Сайт из архива
    """
    name = models.CharField(max_length=99)
    url = models.URLField(max_length=200)
    image = models.ImageField(upload_to='img', height_field=None, width_field=None, max_length=200)

    def __str__(self):
        return self.name


class Domain(models.Model):
    """
    Домен
    """
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
    """
    Примеры кода Html, Css, JS
    """
    name = models.CharField(max_length=99, verbose_name='Пример кода')
    html_code = models.TextField(verbose_name='Html код', blank=True)
    css_code = models.TextField(verbose_name='Css код', blank=True)
    js_code = models.TextField(verbose_name='Js код', blank=True)

    def __str__(self):
        return self.name



class LearnCode(models.Model):
    LANGS = (
        ('JS', 'JS'),
        ('HTML', 'HTML'),
        ('CSS', 'CSS'),
        ('Python', 'Python'),
        ('Git', 'Git'),
        ('Sql', 'Sql'),
    )
    group = models.CharField(max_length=200, choices=LANGS)
    example = models.TextField()
    descriptions = models.TextField()

    def __str__(self):
        return self.example
