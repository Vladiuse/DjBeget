from abc import ABC

from bs4 import BeautifulSoup

from .api import Connection
from langdetect import detect


class StatusHTML:
    GREY = 'btn btn-secondary'
    RED = 'btn btn-danger'
    YELLOW = 'btn btn-warning'
    GREEN = 'btn btn-success'


class Url:
    """
    Формирует все url
    """
    SUCCESS_PAGE = 'success/success.html'
    POLICY = 'policy.html'
    SPAS = 'spas.html'
    TERM = 'terms.html'

    def __init__(self, url, **kwargs):
        self.url = url + '' if url.endswith('/') else '/'
        self.success_url = self.url + Url.SUCCESS_PAGE
        self.policy_url = self.url + Url.POLICY
        self.spas_url = self.url + Url.SPAS
        self.term_url = self.url + Url.TERM

    def get_url(self):
        return self.url

    def get_success_url(self):
        return self.success_url

    def get_policy_url(self):
        return self.policy_url

    def get_spas_url(self):
        return self.spas_url

    def get_term_url(self):
        return self.term_url


class Checker(Connection, ABC):
    """
    Проверочник ссылок
    """
    NO_TITLE_ON_PAGE = 'Заголовок не найден'
    TITLE_FIND = ''

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.soup = None
        self.text = None
        self.result = {}

    def make_soup(self):
        self.conn(self.url)
        self.text = self.response.text
        self.soup = BeautifulSoup(self.response.text, 'lxml')

    def get_h1_title(self):
        # page_title = ''
        # for number in range(1, 4):
        #     tag = 'h' + str(number)
        #     page_title += self.soup.find(tag)
        #     if page_title:
        #         break
        # return page_title if page_title else Checker.NO_TITLE_ON_PAGE
        title = self.soup.find('title')
        if not title:
            return self.NO_TITLE_ON_PAGE
        return title.text

    def get_lang_of_page(self):
        return detect(self.soup.text)

    # @abstractmethod
    def process(self):
        pass

    def get_result(self):
        return self.result

    @staticmethod
    def find_text_block(text, start, end):
        start_pos = text.find(start)
        end_pos = text.find(end, start_pos + 1)
        if start_pos != -1 and end_pos != -1:
            return text[start_pos + len(start):end_pos]


class MainPage(Checker):

    """
    Обработчик главной страницы
    """

    REQUISITES = ['ИП Гребенщиков', 'УНП 19345252', 'Радиальная']
    ORDER_ACTION = 'api.php'
    COMMENT_ACTION = 'spas.html'
    FORM_NAME = 'name="name"'
    FORM_PHONE = 'name="phone"'
    SAVED_FROM = '<!-- saved from'
    I_AGREE = 'Я согласен с политикой конфиденциальности и пользовательским соглашением'

    # INFO
    SAVE_COMM_IN = 'Комментарий saved from на странице'
    SAVE_COMM_NOT_IN = 'Нет коментрария saved from'
    REQUISITES_IN_PAGE = 'Присутствуют'
    REQUISITES_ERROR = 'Не коректные реквизиты'
    ORDER_FORMS_CORRECT = 'Формы заказа корректны'
    ORDER_FORMS_INCORRECT = 'Ошибка в форме заказа: '
    INCORRECT_NO_IN_LAND = 'Отсутствуют'
    INCORRECT_IN_LAND = 'Есть некорректные формы'
    SPAS_FORM_IN = 'Форма отзыва есть'
    SPAS_FORM_NO = 'Нет формы отзыва'

    def __init__(self, url):
        super().__init__(url=url)
        self.forms = {
            'order_forms': [],
            'spas_forms': [],
            'incorrect_forms': [],
        }

    def check_requisites(self):
        """Проверка наличия реквизитов на странице"""
        req_res = all(req in self.soup.text for req in MainPage.REQUISITES)
        status = StatusHTML.GREEN if req_res else StatusHTML.YELLOW
        req_res = MainPage.REQUISITES_IN_PAGE if req_res else MainPage.REQUISITES_ERROR
        self.result.update({'requisites': {'status': status, 'info': req_res}})

    def process(self):
        self.make_soup()

        self.check_requisites()
        self.find_forms()
        self.check_forms()
        self.find_save_comm()
        self.check_lang()

        self.get_forms_result()

    def check_lang(self):
        lang = self.get_lang_of_page()
        self.result.update({'main_page_lang': {'status': StatusHTML.GREEN, 'info': lang}})

    def find_save_comm(self):
        if self.SAVED_FROM in self.response.text:
            status = StatusHTML.YELLOW
            res = self.SAVE_COMM_IN
        else:
            res = self.SAVE_COMM_NOT_IN
            status = StatusHTML.GREEN
        self.result.update({'html_comment': {'info': res, 'status': status}})

    def find_forms(self):
        forms = self.soup.find_all('form')
        for form in forms:
            if form.get('action') == MainPage.ORDER_ACTION:
                self.forms['order_forms'].append(form)
            elif form.get('action') == MainPage.COMMENT_ACTION:
                self.forms['spas_forms'].append(form)
            else:
                self.forms['incorrect_forms'].append(form)

    def check_forms(self):
        """Провверка формы заказа"""
        order_forms = self.forms['order_forms']
        result = []
        for form in order_forms:
            name = phone = checkbox = checkbox_text = False
            inputs = form.find('input', {'type': 'checkbox'})
            if inputs:
                checkbox = True
            form_text = ''.join(form.text.rsplit())
            I_AGREE = ''.join(self.I_AGREE.rsplit())
            if I_AGREE in form_text:
                checkbox_text = True
            form = str(form)
            if MainPage.FORM_NAME in form:
                name = True
            if MainPage.FORM_PHONE in form:
                phone = True
            result.append(all([name, phone, checkbox, checkbox_text]))
        self.forms['order_forms'] = result

    def get_forms_result(self):
        """Получение результата проверки форм"""
        # orders
        if all(self.forms['order_forms']):
            form_count = len(self.forms['order_forms'])
            self.forms['order_forms'] = {'status': StatusHTML.GREEN, 'info': MainPage.ORDER_FORMS_CORRECT + f': {form_count}шт.'}
        else:
            number_incorrect_form = ','.join(str(id + 1) for id, x in enumerate(self.forms['order_forms']) if x)
            self.forms['order_forms'] = {'status': StatusHTML.RED,
                                         'info': MainPage.ORDER_FORMS_INCORRECT + number_incorrect_form}
        # incorrect
        if not self.forms['incorrect_forms']:
            self.forms['incorrect_forms'] = {'status': StatusHTML.GREEN, 'info': MainPage.INCORRECT_NO_IN_LAND}
        else:
            self.forms['incorrect_forms'] = {'status': StatusHTML.YELLOW, 'info': MainPage.INCORRECT_IN_LAND}
        # spas forms
        if self.forms['spas_forms']:
            spas_form_count = len(self.forms['spas_forms'])
            self.forms['spas_forms'] = {'status': StatusHTML.GREEN, 'info': MainPage.SPAS_FORM_IN + f': {spas_form_count}шт.'}
        else:
            self.forms['spas_forms'] = {'status': StatusHTML.YELLOW, 'info': MainPage.SPAS_FORM_NO}

        self.result.update(self.forms)

    def get_spas_forms(self):
        return self.forms['spas_forms']


class SpasPage(Checker):
    """
    Обработчик страницы отзыва
    """
    CORRECT = 'Редирект натроен'
    FIND = """eval(self.location = "https://" + location.hostname + '/');"""
    INCORRECT = 'Ошибка - не корректный url для редиректа'
    SPAS_PAGE_WORK = 'Страница отзыва работает'
    SPAS_PAGE_NOT_WORK = 'Страница отзыва НЕ  работает'

    def process(self):
        self.check_spas_page()
        self.find_url_in_page()

    def find_url_in_page(self):
        """Поиск сссылки spas.html на главной странице"""
        self.conn(self.url)
        # url = self.url.replace(Url.SPAS, '')]
        url_in_page = self.FIND in self.response.text
        result = SpasPage.CORRECT if url_in_page else SpasPage.INCORRECT
        status = StatusHTML.GREEN if url_in_page else StatusHTML.YELLOW
        self.result.update({'spas_page_res': {'status': status, 'info': result}})

    def check_spas_page(self):
        self.conn(self.url)
        if self.status_code == 200:
            spas_page_result = self.SPAS_PAGE_WORK
            status = StatusHTML.GREEN
        else:
            status = StatusHTML.RED
            spas_page_result = self.SPAS_PAGE_NOT_WORK
        self.result.update({'spas_page': {'status': status, 'info': spas_page_result}})


class PolicyPage(MainPage):
    """
    Обработчик policy page
    """
    POLICY_LINK = 'policy.html'
    P_ON_PAGE = 'Полиси найдет'
    NO_P_ON_PAGE = 'Полиси не найден'
    P_PAGE_WORK = 'Страница полиси работает'
    P_PAGE_NOT_WORK = 'Страница полиси  НЕ работает'

    def process(self):

        self.find_policy_link()
        self.check_policy_page()

    def check_policy_page(self):
        self.conn(self.url)
        if self.status_code == 200:
            policy_page_result = self.P_PAGE_WORK
            status = StatusHTML.GREEN
        else:
            policy_page_result = self.P_PAGE_NOT_WORK
            status = StatusHTML.RED
        self.result.update({'policy_page': {'status': status, 'info': policy_page_result}})

    def find_policy_link(self):
        """Поиск """
        link = self.soup.find('a', href=PolicyPage.POLICY_LINK)
        link_on_page = self.P_ON_PAGE if link else self.NO_P_ON_PAGE
        status = StatusHTML.GREEN if link else StatusHTML.YELLOW
        self.result.update({'policy_link': {'status': status, 'info': link_on_page}})


class TermsPage(MainPage):
    """
        Обработчик terms page
    """
    TERM_LINK = 'terms.html'
    T_ON_PAGE = 'Terms on page'
    T_NOT_ON_PAGE = 'terms not on page'
    T_PAGE_WORK = 'Страница соглашений работает'
    T_PAGE_NOT_WORK = 'Страница соглашений  НЕ работает'

    def process(self):
        self.find_term_link()
        self.check_terms_page()

    def check_terms_page(self):
        """проверка ссылки"""
        self.conn(self.url)
        if self.status_code == 200:
            terms_page_result = self.T_PAGE_WORK
            status = StatusHTML.GREEN
        else:
            terms_page_result = self.T_PAGE_NOT_WORK
            status = StatusHTML.RED
        self.result.update({'term_page': {'status': status, 'info': terms_page_result}})

    def find_term_link(self):
        """Поиск ссылки пользовательского соглашения"""
        link = self.soup.find('a', href=TermsPage.TERM_LINK)
        link_on_page = self.T_ON_PAGE if link else self.T_NOT_ON_PAGE
        status = StatusHTML.GREEN if link else StatusHTML.YELLOW
        self.result.update({'term_link': {'status': status, 'info': link_on_page}})


class SuccessPage(Checker):
    """
    Обработчик success page
    """

    FBP_DESCRIPTION = {'start': '<!-- Facebook Pixel Code -->', 'end': '<!-- End Facebook Pixel Code -->'}
    FBP_1 = {'start': "fbq('init', '",
             'end': "');\nfbq('track'"}
    FBP_2 = {'start': "https://www.facebook.com/tr?id=",
             'end': "&ev"}
    # INFO
    different_pixels = 'Different pixels in land'
    no_pixel_block = 'No pixel block'
    correct_pixel = 'Correct FB pixel'

    def __init__(self, url, pixel=None):
        super().__init__(url=url)
        self.pixel = str(pixel) if pixel else pixel
        self.pixel_in_land = None

    def find_fb_pixel(self):
        """
        Поикс пикселя на странице, если указан - проверка на соответствие
        """
        pixel_block = self.find_text_block(self.text,
                                           SuccessPage.FBP_DESCRIPTION['start'], SuccessPage.FBP_DESCRIPTION['end'])
        if pixel_block:
            fbp_1 = self.find_text_block(pixel_block, SuccessPage.FBP_1['start'], SuccessPage.FBP_1['end'])
            fbp_2 = self.find_text_block(pixel_block, SuccessPage.FBP_2['start'], SuccessPage.FBP_2['end'])
            if fbp_1 == fbp_2:
                self.pixel_in_land = fbp_1
            else:
                self.pixel_in_land = SuccessPage.different_pixels
        else:
            self.pixel_in_land = SuccessPage.no_pixel_block

    def process(self):
        self.make_soup()
        self.find_fb_pixel()
        if self.pixel == self.pixel_in_land:
            pixel_res = SuccessPage.correct_pixel
            status = StatusHTML.GREEN
        else:
            pixel_res = self.pixel_in_land
            # status = StatusHTML.YELLOW
            status = StatusHTML.GREEN
        self.result.update({'pixel': {'status': status, 'info': pixel_res}})


class LinkCheckerManager:
    """
    Менеджер страниц
    """

    def __init__(self, url, **kwargs):
        self.url_class = Url(url=url)
        self.main_page = MainPage(url=self.url_class.get_url(), )
        self.policy_page = PolicyPage(url=self.url_class.get_policy_url())
        self.success_page = SuccessPage(url=self.url_class.get_success_url(), **kwargs)
        self.spas_page = SpasPage(url=self.url_class.get_spas_url())
        self.term_page = TermsPage(url=self.url_class.get_term_url())
        self.result = {
            'requisites': {},
            'order_forms': {},
            'spas_forms': {},
            'incorrect_forms': {},
            'policy_link': {},
            'policy_page': {},
            'pixel': {},
            'term_link': {},
            'term_page': {},
            'spas_page': {},
            'spas_page_res': {},
            'html_comment': {},
            'main_page_lang': {},
        }

    def process(self):
        self.main_page.process()
        # add soup to ...
        self.policy_page.soup = self.main_page.soup
        self.term_page.soup = self.main_page.soup
        self.spas_page.soup = self.main_page.soup

        self.success_page.process()
        self.policy_page.process()
        self.term_page.process()
        self.spas_page.process()

        self.collect_results()

    def collect_results(self):
        """Сбор данных проверки со всех классов"""
        for item in self.main_page, self.policy_page, self.success_page, self.spas_page, self.term_page:
            self.result.update(item.get_result())

    def get_general_result(self):
        try:
            stats = set([status['status'] for status in self.result.values()])
        except KeyError:
            return StatusHTML.GREY
        else:
            if StatusHTML.RED in stats:
                return StatusHTML.RED
            elif StatusHTML.YELLOW in stats:
                return StatusHTML.YELLOW
            else:
                return StatusHTML.GREEN

