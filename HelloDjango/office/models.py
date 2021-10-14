from django.db import models
from django.utils import timezone

# Create your models here.
from .api import MyError, Beget
from .link_checker import Checker


class Site(models.Model):
    """
    Сайт
    """
    DONT_CHECK = ['vladiuse.beget.tech', 'django', 'old-lands', ]
    NOT_TITLE = ['None', MyError.NO_CONNECTION, '404 Not Found',
                 'Домен не прилинкован ни к одной из директорий на сервере!',
                 'Новый сайт успешно создан и готов к работе', ]

    GREY = 'Не проверен'
    RED = 'Ошибка'
    YELLOW = 'Замечание'
    GREEN = 'Все ок'

    STATUS_HTML = {
        GREY: 'btn btn-secondary',
        RED: 'btn btn-danger',
        YELLOW: 'btn btn-warning',
        GREEN: 'btn btn-success',
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
    title = models.CharField(max_length=200, verbose_name='Заголовок сайта', default='None')
    check_status = models.CharField(max_length=200, choices=CHOICE, default=GREY, verbose_name='Статус проверки сайта')
    check_data = models.JSONField(default=dict)
    datetime = models.DateTimeField(auto_now_add=True)
    is_camp_run = models.BooleanField(default=False)
    is_cloac = models.BooleanField(default=False)

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
        try:
            return self.STATUS_HTML[str(self.check_status)]
        except KeyError:
            return 'No status key error'


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
        if self.is_cloac:
            url = self.black_page()
        page = Checker(url=url)
        try:
            page.make_soup()
        except MyError:
            self.title = MyError.NO_CONNECTION
        else:
            self.title = page.get_h1_title()
        self.save()

    def check_cloac(self):
        """Определить заклоачена ссылка или нет - есть ли в action формы s_api.php"""
        url = self.get_http_site()
        page = Checker(url=url)
        try:
            page.make_soup()
        except MyError:
            self.title = MyError.NO_CONNECTION
        else:
            soup = page.soup
            forms = soup.find_all('form')
            for f in forms:
                if f.get('action') == 's_api.php':
                    self.is_cloac = True
                    self.save()
                    break

    def black_page(self):
        """Получить ссылку на скрытую страницу"""
        return self.get_http_site() + 'black.html'

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

    def set_site_run(self):
        print('RUN')
        self.is_camp_run = True
        self.save()
        print(self.is_camp_run)

    def set_site_not_run(self):
        print('RUN OFFF')
        self.is_camp_run = False
        self.save()
        print(self.is_camp_run)

    # def is_camp_run(self):
    #     """Запущена ли кампания с этим сайтом"""
    #     domains = self.domain_set.all()
    #     for dom in domains:
    #         for camp in dom.company_set.all():
    #             if camp.status.name == 'Запущено':
    #                 return True
    #     return False

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

    def beget_edit_link(self):
        return f'https://cp.beget.com/fm/%7B%22type%22:%22home%22,%22path%22:%22/old-lands/public_html/{self.name}%22%7D'

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
        NEW: 'btn btn-success',
        USE: 'btn btn-warning',
        BAN: 'btn btn-danger',
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

    def get_root_domain(self):
        if self.name.count('.') == 2:
            return self.name[self.name.find('.') + 1:]
        return self.name

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


class TrafficSource(models.Model):
    name = models.CharField(max_length=200, verbose_name='Источник трафика')
    short_name = models.CharField(max_length=10, verbose_name='краткое название', unique=True, blank=True, null=True)
    icon_html = models.CharField(max_length=100, verbose_name='Код иконки html', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Источник трафика'
        verbose_name_plural = 'Источники трафика'


class Country(models.Model):
    name_ru = models.CharField(max_length=200, verbose_name='Название страны')
    name_eng = models.CharField(max_length=200, verbose_name='Название страны ENG', blank=True, null=True)
    short_name = models.CharField(max_length=10, verbose_name='Абревивтура страны')
    phone_code = models.IntegerField(verbose_name='Код мобильного страны', unique=True, blank=True, null=True)

    def __str__(self):
        return self.name_ru

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


class CampaignStatus(models.Model):
    name = models.CharField(max_length=200, verbose_name='Статуст кампании')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Cтатус кампании'
        verbose_name_plural = 'Cтатусы кампаний'


class Company(models.Model):
    name = models.CharField(max_length=299, verbose_name='Название кампании', blank=True, null=True)
    cab = models.ForeignKey('Cabinet', on_delete=models.SET_NULL, verbose_name='Кабинет запуска', null=True)
    geo = models.ManyToManyField(Country, verbose_name='Гео запуска')
    land = models.ManyToManyField(Domain, verbose_name='Запускаемая ссылка')
    status = models.ForeignKey(CampaignStatus, on_delete=models.SET_NULL, null=True, blank=True)
    published = models.DateTimeField(auto_now_add=True, )
    edited = models.DateTimeField(auto_now=True, )
    daily = models.CharField(max_length=12, verbose_name='Дневной бюджет', blank=True, null=True)

    class Meta:
        verbose_name = 'Кампания'
        verbose_name_plural = 'Кампании'

    def __str__(self):
        return self.name


class Account(models.Model):
    source = models.ForeignKey(TrafficSource, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200, verbose_name='Название аккаунта', blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True, verbose_name='описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'


class Cabinet(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название кабинета')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    pixel = models.CharField(verbose_name='Пиксель акаунта', blank=True, null=True, max_length=99)
    description = models.CharField(max_length=300, blank=True, null=True, verbose_name='описание')
    # domain = models.OneToOneField(Domain, on_delete=models.SET_NULL, blank=True, null=True,
    #                               verbose_name='Закрепленный домен')
    domain = models.ForeignKey(Domain, on_delete=models.SET_NULL,blank=True, null=True,
                                  verbose_name='Закрепленный домен')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рекламный кабинет'
        verbose_name_plural = 'Рекламные кабинеты'


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


class Test(models.Model):
    DIC_1 = {'result_code': 'error', 'result_html': 'danger', 'result_text': 'Ошибка'}
    DIC_2 = {"result": [{'result_code': 'error', 'result_html': 'danger', 'result_text': 'Ошибка'},
                        {'result_code': 'error', 'result_html': 'danger', 'result_text': 'Ошибка'}]}
    json = models.JSONField()
