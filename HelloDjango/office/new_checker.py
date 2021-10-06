import requests as req
from bs4 import BeautifulSoup


class Page:

    def __init__(self, url):
        self.url = url if not url.endswith('/') else url + '/'
        self.status_code = None
        self.text = None
        self.soup = None

    def is_work(self):
        return self.status_code == 200

    def connect(self):
        try:
            res = req.get(self.url)
            self.status_code = res.status_code
            self.text = res.text
            self.soup = BeautifulSoup(self.text, 'lxml')
        except req.exceptions.ConnectionError:
            print(f'Page dont work: {self.url}')

    def get_text(self):
        return self.text

    def get_soup(self):
        return self.soup()

    def get_text_no_spaces_soup(self):
        """Возвращает текст со страницы без верстки и пробелов"""
        text = self.soup.text.replace(' ', '')
        return text

    @staticmethod
    def find_text_block(text, start, end):
        """Вывод текста межды подстроками"""
        start_pos = text.find(start)
        end_pos = text.find(end, start_pos + 1)
        if start_pos != -1 and end_pos != -1:
            return text[start_pos + len(start):end_pos]


class Site:
    # sitemap
    SUCCESS_PAGE = 'success/success.html'
    POLICY = 'policy.html'
    SPAS = 'spas.html'
    TERM = 'terms.html'
    # if clo
    WHITE = 'white.html'
    BLACK = 'black.html'

    def __init__(self, url):
        self.main = Page(url)
        self.spas = Page(url + Site.SPAS)
        self.policy = Page(url + Site.POLICY)
        self.terms = Page(url + Site.TERM)
        self.success = Page(url + Site.SUCCESS_PAGE)

    def check_pages_conn(self):
        for page in self.main, self.success, self.policy, self.terms, self.spas:
            page.connect()


class StatusHTML:
    GREY = 'status-none'
    RED = 'status-unpaid'
    YELLOW = 'status-pending'
    GREEN = 'status-paid'


class LinkChecker:
    class Check:
        DESCRIPTION = 'No'
        # text_statuses
        NONE = 'Не проверялся'
        GOOD = 'Все ок'
        REPRIMAND = 'Замечание'
        ERROR = 'Ошибка'

        def __init__(self, site):
            self.site = site
            self.description = self.DESCRIPTION
            self.result_text = ''
            self.info = []  # доп. информация (для ошибок)
            self.errors = []  # вывод примеров ошибок
            # self.statusHtml = None
            self.is_check = False
            self.result_code = ''
            # self.result = Result(description=self.DESCRIPTION)

        def process(self):
            pass

        def set_checked(self):
            self.is_check = True

        def set_reprimand(self):
            self.result_text = self.REPRIMAND

        def set_all_good(self):
            self.result_text = self.GOOD

        def set_error(self):
            self.result_text = self.ERROR

        def set_none(self):
            self.result_text = self.NONE

    class Req(Check):
        DESCRIPTION = 'Реквизиты'

        INCORRECT_REQ = 'Есть некоректные'

        STATUS_SET = {
            INCORRECT_REQ: 'reprimand',
        }

        REQUISITES = {
            'name': 'ИП Гребенщиков',
            'unp': 'УНП 19345252',
            'address': 'г.Минск, ул. Радиальная, д. 40',
            'email': 'E-mail: zenitcotrade@gmail.com',
            'phone': 'Телефон: +375 29 679-00-99',
        }

        def process(self):
            self.find_req_fb()

        def find_req_fb(self):
            """Поиск реквизитов FaceBook"""
            FB_REQ = 'name', 'unp', 'address'
            self.find_reqs(FB_REQ)

        def find_req_tt(self):
            """Поиск реквизитов TikTok"""
            TT_REQ = self.REQUISITES.keys()
            self.find_reqs(TT_REQ)

        def find_reqs(self, reqs):
            # errors = []
            page_text = self.site.main.get_text_no_spaces_soup()
            for req in reqs:
                req_text = self.REQUISITES[req].replace(' ', '')
                if req_text not in page_text:
                    self.info.append(req)
            if not self.info:
                self.set_all_good()
            else:
                # self.info = ','.join(errors)
                self.set_reprimand()

    class SaveComment(Check):
        """Поиск коментария от google chrome"""
        DESCRIPTION = 'Реквизиты'
        SAVED_FROM = '<!-- saved from'

        COMM_ON_PAGE = 'Комментарий saved from на странице'

        STATUS_SET = {
            COMM_ON_PAGE: 'reprimand',
        }

        def process(self):
            self.find_comm()

        def find_comm(self):
            text = self.site.main.get_text()
            lines = text.split('\n')[:5]
            for line in lines:
                if self.SAVED_FROM in line:
                    self.set_reprimand()
                    return
            self.set_all_good()

    class PolicyPage(Check):
        DESCRIPTION = 'Страница политики конфиденциальности'
        POLICY_LINK = 'policy.html'
        LINK_TEXT = 'Политика конфиденциальности'

        INCORRECT_TEXT = 'Ошибка в подписи ссылки'
        NO_LINK = 'Нет ссылки на странице'
        PAGE_NOT_WORK = 'Страница не работает'

        STATUS_SET = {
            INCORRECT_TEXT: 'reprimand',
            NO_LINK: 'reprimand',
            PAGE_NOT_WORK: 'reprimand',
        }

        def process(self):
            self.find_link()
            self.check_page()
            if not self.info:
                self.set_reprimand()
            else:
                self.set_all_good()

        def find_link(self):
            soup = self.site.main.get_soup()
            link = soup.find('a', href=self.POLICY_LINK)
            if link:
                if self.LINK_TEXT not in link.text:
                    self.info.append(self.INCORRECT_TEXT)
            else:
                self.info.append(self.NO_LINK)

        def check_page(self):
            if not self.site.main.is_work():
                self.info.append(self.PAGE_NOT_WORK)

    class TermsPage(PolicyPage):
        DESCRIPTION = 'Страница пользовательского соглашения'
        POLICY_LINK = 'terms.html'
        LINK_TEXT = 'Пользовательское соглашение'

    class SpasPage(Check):
        """
        Обработчик страницы отзыва
        """
        DESCRIPTION = 'Страница отзыва'
        CORRECT = 'Редирект натроен'
        ACTION = 'spas.html'
        FIND = """eval(self.location = "https://" + location.hostname + '/');"""

        INCORRECT_REDIRECT = 'Ошибка - не корректный url для редиректа'
        PAGE_NOT_WORK = 'Страница отзыва НЕ работает'
        NO_SPAS_FORM = 'Нет формы отзыва'

        STATUS_SET = {
            INCORRECT_REDIRECT: 'error',
            PAGE_NOT_WORK: 'reprimand',
            NO_SPAS_FORM: 'reprimand',
        }

        def process(self):
            self.check_form()
            self.check_page()
            self.find_redirect_url()
            if self.info:
                self.set_reprimand()
            # else:
            #     self.set_all_good()

        def check_form(self):
            soup = self.site.spas.get_soup()
            form = soup.find('form', action=self.ACTION)
            if not form:
                self.info.append(self.NO_SPAS_FORM)

        def check_page(self):
            if not self.site.spas.is_work:
                self.info.append(self.PAGE_NOT_WORK)

        def find_redirect_url(self):
            if self.FIND not in self.site.spas.get_text():
                self.info.append(self.INCORRECT_REDIRECT)

    class SuccessPage(Check):
        DESCRIPTION = 'Итоговая страница'

        PAGE_NOT_WORK = 'Страница не работает'

        STATUS_SET = {
            PAGE_NOT_WORK: 'error',
        }

        def process(self):
            self.check_page()
            # if not self.info:
            #     self.set_reprimand()
            # else:
            #     self.set_all_good()

        def check_page(self):
            if not self.site.success.is_work():
                self.info.append(self.PAGE_NOT_WORK)

    class FaceBookPixel(Check):
        """Пиклесль ФБ"""
        DESCRIPTION = 'Пиклесль ФБ'
        FBP_DESCRIPTION = {'start': '<!-- Facebook Pixel Code -->', 'end': '<!-- End Facebook Pixel Code -->'}
        FBP_1 = {'start': "fbq('init', '",
                 'end': "');"}
        FBP_2 = {'start': "https://www.facebook.com/tr?id=",
                 'end': "&ev"}

        PIXEL_NOT_FOUND = 'Пиксель не найден'
        ONE_NOT_CORRECT = 'Один из пикселей некоректен'

        STATUS_SET = {
            PIXEL_NOT_FOUND: 'reprimand',
            ONE_NOT_CORRECT: 'reprimand',
        }

        def process(self):
            self.find_pixel()
            # if not self.info:
            #     self.set_reprimand()
            # else:
            #     self.set_all_good()

        def find_pixel(self):
            pixel_block = Page.find_text_block(self.site.success.get_text(),
                                               self.FBP_DESCRIPTION['start'], self.FBP_DESCRIPTION['end'])
            if pixel_block:
                fbp_1 = Page.find_text_block(pixel_block, self.FBP_1['start'], self.FBP_1['end'])
                fbp_2 = Page.find_text_block(pixel_block, self.FBP_2['start'], self.FBP_2['end'])
                if fbp_1 != fbp_2:
                    self.info.append(self.ONE_NOT_CORRECT)
                else:
                    self.result_text = fbp_1
            else:
                self.info.append(self.PIXEL_NOT_FOUND)

    class TtPixel(Check):
        DESCRIPTION = 'Пиклесль TikTok'
        TT = {'start': "ttq.load('",
              'end': "');"}

        PIXEL_NOT_FOUND = 'Пиксель не найден'

        STATUS_SET = {
            PIXEL_NOT_FOUND: 'reprimand',
        }

        def process(self):
            self.find_pixel()
            # if not self.info:
            #     self.set_reprimand()
            # else:
            #     self.set_all_good()

        def find_pixel(self):
            tt_pixel = Page.find_text_block(self.site.success.get_text(), self.TT['start'], self.TT['end'])
            if not tt_pixel:
                self.info.append(self.PIXEL_NOT_FOUND)
            else:
                self.result_text = tt_pixel

    class PageLink(Check):
        """Поиск некоректных внутрених ссылок"""
        DESCRIPTION = 'Внутрение сслыки'
        DO_NOT_CHECK = {'policy.html', 'terms.html', 'spas.html'}

        FIND_ALIEN = 'Есть ссылки на чужой лэнд'
        INCORRECT_INNER = 'Некоректные внутриние ссылки'
        NO_HREF = 'Есть ссылки без href'

        STATUS_SET = {
            FIND_ALIEN: 'error',
            INCORRECT_INNER: 'reprimand',
            NO_HREF: 'reprimand',
        }

        def process(self):
            self.find_links()

        def find_links(self):
            soup = self.site.main.get_soup()
            links = soup.find_all('a')
            for link in links:
                try:
                    href = link['href']
                    if not (href.startswith('#') or href in self.DO_NOT_CHECK):
                        if href.startswith('http'):
                            self.info.append(self.FIND_ALIEN)
                            self.errors.append(href)
                        else:
                            self.info.append(self.INCORRECT_INNER)
                            self.errors.append(href)
                except KeyError:
                    self.info.append(self.NO_HREF)

    class HTMLForm:
        """html форма"""

        def __init__(self, form_soup):
            self.form = form_soup
            self.action = None
            self.name = None
            self.phone = None
            self.phone_minlength = None
            self.i_agree = None

        def process(self):
            self.find_action()
            self.find_name()
            self.find_phone()
            self.get_phone_minlength()

        def find_action(self):
            try:
                self.action = self.form['action']
            except KeyError:
                self.action = 'not found'

        def find_name(self):
            name = self.form.find('input', {'name': 'name'})
            if name:
                self.name = name.get('name')

        def find_phone(self):
            phone = self.form.find('input', {'name': 'phone'})
            if phone:
                self.phone = phone.get('name')

        def get_phone_minlength(self):
            if self.phone:
                phone = self.form.find('input', {'name': 'phone'})
                try:
                    self.phone_minlength = phone['minlength']
                except KeyError:
                    pass

        def check_i_agree_input(self):
            pass

    class OrderForms(Check):
        DESCRIPTION = 'Order формы'

        NO_FORMS = 'Формы не найдены'
        # INCORRECT_FROM = 'Есть некоректная форма'
        # NO_ACTION = 'Отсутствует action в форме'
        INCORRECT_ACTION = 'Некоректный action в форме'
        NAME_ERROR = 'Нет инпута(ошибка) для имени'
        PHONE_ERROR = 'Нет инпута(ошибка) для телефона'
        NO_MIN_LEN = 'Минимальная длина номера не установлена'

        STATUS_SET = {
            NO_FORMS: 'error',
            INCORRECT_ACTION: 'error',
            NAME_ERROR: 'error',
            PHONE_ERROR: 'error',
            NO_MIN_LEN: 'reprimand',
        }

        def __init__(self, site):
            super().__init__(site=site)
            self.forms = []
            self.order_forms_count = 0

        def process(self):
            self.find_forms()
            for form in self.forms:
                self.check_order_form(form)
            if not self.order_forms_count:
                self.info.append(self.NO_FORMS)

        def find_forms(self):
            soup = self.site.main.get_soup()
            forms = soup.find_all('form')
            for form in forms:
                self.forms.append(LinkChecker.HTMLForm(form))

        def check_order_form(self, form):
            form.process()
            if form.action != 'spas.html':
                self.order_forms_count += 1
                if form.action != 'api.php':
                    self.info.append(self.INCORRECT_ACTION)
                if form.name != 'name':
                    self.info.append(self.NAME_ERROR)
                if form.phone != 'phone':
                    self.info.append(self.PHONE_ERROR)
                if not form.phone_minlength:
                    self.info.append(self.NO_MIN_LEN)

    # тело Главного чекера
    def __init__(self, site):
        self.site = site
        self.checkers = [
            self.Req,
            self.OrderForms,
        ]
        self.result = []

    def process(self):
        self.site.check_pages_conn()
        for check in self.checkers:
            check(self.site).process()


if __name__ == '__main__':
    pass
