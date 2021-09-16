from django.db import models
from django.utils import timezone

# Create your models here.
from .api import MyError, Beget
from .link_checker import Checker


class Site(models.Model):
    """
    Сайт
    """
    DONT_CHECK = ['vladiuse.beget.tech', 'django', 'old-lands',]
    NOT_TITLE = ['None', MyError.NO_CONNECTION, '404 Not Found',
                 'Домен не прилинкован ни к одной из директорий на сервере!']

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
    beget_id = models.IntegerField()
    site_name = models.CharField(max_length=99)
    # domain = models.URLField(max_length=200, verbose_name='Ссылка сайта')
    title = models.CharField(max_length=200, verbose_name='Заголовок сайта')
    check_status = models.CharField(max_length=200, choices=CHOICE, default=GREY, verbose_name='Статус проверки сайта')
    datetime = models.DateTimeField(auto_now_add=True)

    def save(self):
        # TODO перенести в другую функцию?
        public_dir = '/public_html'
        if self.site_name.endswith(public_dir):
            self.site_name = self.site_name[:-len(public_dir)]
        super().save()

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
        if self.site_name in Site.DONT_CHECK:
            return
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
        return self.get_http_site() + 'log.txt'

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

    def is_new(self):
        return (timezone.now() - self.datetime) < timezone.timedelta(days=1)

    def get_id_beget(self):
        b = Beget()
        sites = b.get_sites()
        for site in sites['result']:
            id = site['id']
            print(id)
            name = site['path'].split('/')[0]
            print(name)
            site_in_base = Site.objects.get(site_name=name)
            site_in_base.beget_id = id
            site_in_base.save()

    def domain_count(self):
        return len(self.domain_set.all())

    def is_domain_link(self):
        return bool(len(self.domain_set.all()))

    def __str__(self):
        return self.site_name


class TrafficSource(models.Model):
    name = models.CharField(max_length=200, verbose_name='Источник трафика')
    short_name = models.CharField(max_length=10, verbose_name='краткое название', unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Источники трафика'
        verbose_name_plural = 'Источник трафика'


class Country(models.Model):
    name_ru = models.CharField(max_length=200, verbose_name='Название страны')
    name_eng = models.CharField(max_length=200, verbose_name='Название страны ENG', blank=True, null=True)
    short_name = models.CharField(max_length=10, verbose_name='Абревивтура страны')
    phone_code = models.IntegerField(verbose_name='Код мобильного страны', unique=True, blank=True, null=True)

    def __str__(self):
        return self.name_ru

    class Meta:
        verbose_name = 'Страны'
        verbose_name_plural = 'Страна'


class CampaignStatus(models.Model):
    name = models.CharField(max_length=200, verbose_name='Статуст кампании')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Cтатусы кампаний'
        verbose_name_plural = 'Cтатус кампании'


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
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=99, verbose_name='название домена', unique=True)
    # url = models.URLField(max_length=300, blank=True, null=True, unique=True)
    beget_id = models.IntegerField(verbose_name='id домена на beget', unique=True)
    description = models.TextField(max_length=999, verbose_name='доп. информация', blank=True)

    # some info
    facebook = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=NEW)
    google = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=NEW)
    tiktok = models.CharField(max_length=99, choices=DOMAIN_STATUS, default=NEW)

    def get_http(self):
        return f'http://{self.name}/'

    def get_html_facebook(self):
        return Domain.HTML_CLASS[self.facebook]

    def get_html_google(self):
        return Domain.HTML_CLASS[self.google]

    def get_html_tiktok(self):
        return Domain.HTML_CLASS[self.tiktok]

    def get_http_site(self):
        return f'http://{self.name}/'

    def get_https_site(self):
        return f'https://{self.name}/'

    def __str__(self):
        return self.name


class Account(models.Model):
    source = models.ForeignKey(TrafficSource, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200, verbose_name='Название аккаунта', blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True, verbose_name='описание')

    def __str__(self):
        return self.name

class Cabinet(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название кабинета')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    pixel = models.IntegerField(verbose_name='Пиксель акаунта', blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True, verbose_name='описание')

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
