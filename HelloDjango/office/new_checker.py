import paramiko
import requests as req
from bs4 import BeautifulSoup


class StatusHTML:
    # HTML
    GREY = 'secondary'
    RED = 'danger'
    YELLOW = 'warning'
    GREEN = 'success'
    # Text
    GOOD = 'Все ок'
    REPRIMAND = 'Замечание'
    ERROR = 'Ошибка'
    DISABLED = 'Отключен'
    NONE = 'Не проверен'

    # result_code

    @staticmethod
    def get_checker_status_html(status):
        dic = {
            'good': StatusHTML.GREEN,
            'reprimand': StatusHTML.YELLOW,
            'error': StatusHTML.RED,
            'disabled': StatusHTML.GREY,
            'none': StatusHTML.GREY,
        }
        try:
            html_status = dic[status]
        except KeyError:
            html_status = 'html-key-error'
        return html_status

    @staticmethod
    def get_checker_status_text(status):
        dic = {
            'good': StatusHTML.GOOD,
            'reprimand': StatusHTML.REPRIMAND,
            'error': StatusHTML.ERROR,
            'disabled': StatusHTML.DISABLED,
            'none': StatusHTML.NONE,
        }
        try:
            html_status = dic[status]
        except KeyError:
            html_status = 'text_key_error'
        return html_status


class Page:

    def __init__(self, url):
        self.url = url
        self.status_code = None
        self.text = None
        self.soup = None

    def is_work(self):
        return self.status_code == 200

    def connect(self):
        try:
            res = req.get(self.url)
            res.encoding = 'utf-8'
            self.status_code = res.status_code
            self.text = res.text
            self.soup = BeautifulSoup(res.text, 'lxml')
            print(f'Page work: {self.url}')
            return True
        except req.exceptions.ConnectionError:
            print(f'Page dont work: {self.url}')
            return False

    def get_page_status_code(self):
        return self.status_code

    def get_text(self):
        return self.text

    def get_soup(self):
        return self.soup

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

class SHHConnector:

    def __init__(self):
        self.host = 'vladiuse.beget.tech'
        self.username = 'vladiuse'
        self.password = '20003000Ab%'
        self.port = 22
        self.connection = None
        # подключение
        self.connect()

    def connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, self.port, self.username, self.password)
        self.connection = ssh

    def ls_comm(self, command):
        stdin, stdout, stderr = self.connection.exec_command(f'ls {command}')
        return stdout

    def cat_comm(self, command):
        stdin, stdout, stderr = self.connection.exec_command(f'cat {command}')
        return stdout


class PageFile:

    def __init__(self, file_name, connector):
        self.file_name = file_name
        self.connector = connector
        self.text = None
        self.soup = None

    def connect(self):
        file = self.connector.cat_comm(self.file_name)
        text = str(file.read())
        if text:
            self.text = text
            self.soup = BeautifulSoup(self.text, 'lxml')

    @staticmethod
    def get_variable_value(line):
        if '=' not in line:
            return None
        variable, value = line.split('=')
        value = value.strip()
        if value.endswith(';'):
            value = value[:-1]
        if value.startswith('"') and value.endswith('"'):
            return value.strip('"')
        if value.startswith("'") and value.endswith("'"):
            return value.strip("'")
        return value

class Site:
    SUCCESS_PAGE = '/success/success.html'
    POLICY = '/policy.html'
    SPAS = '/spas.html'
    TERM = '/terms.html'
    # if clo
    WHITE = '/white.html'
    BLACK = '/black.html'
    # files
    CLOAC = 'index.php'
    ORDER = 'api.php'
    SSH_CONNECTOR = SHHConnector()

    def __init__(self, url, is_cloac=False, dir_name=None):
        self.cloac = is_cloac
        # sitemap
        self.main = Page(url) if not is_cloac else Page(url + Site.BLACK)
        self.spas = Page(url + Site.SPAS)
        self.policy = Page(url + Site.POLICY)
        self.terms = Page(url + Site.TERM)
        self.success = Page(url + Site.SUCCESS_PAGE)
        self.black = Page(url + Site.BLACK)
        self.white = Page(url + Site.WHITE)
        # site_files
        self.dir_name = dir_name
        self.files = set()
        self.index_php = PageFile(dir_name + '/' + Site.CLOAC, connector=Site.SSH_CONNECTOR) if self.dir_name else None
        self.api_php = PageFile(dir_name + '/' + Site.ORDER, connector=Site.SSH_CONNECTOR) if self.dir_name else None

    def check_pages_conn(self):
        for page in self.main, self.success, self.policy, self.terms, self.spas:
            page.connect()
        if self.dir_name:
            for page_file in self.index_php, self.api_php:
                page_file.connect()
            self.get_site_files()

    def get_site_files(self):
        data = self.SSH_CONNECTOR.ls_comm(self.dir_name)
        for file_name in data.readlines():
            if file_name.endswith('\n'):
                file_name = file_name[:-1]
            if '.' in file_name:
                self.files.add(file_name)


class LinkChecker:
    class Check:
        DESCRIPTION = 'No'
        # text_statuses
        NONE = 'Не проверялся'
        GOOD = 'Все ок'
        REPRIMAND = 'Замечание'
        ERROR = 'Ошибка'

        STATUS_SET = {}

        def __init__(self, site):
            self.site = site
            self.description = self.DESCRIPTION
            self.result_text = ''
            self.info = set()  # информация об ошибоке
            self.errors = set()  # вывод примеров ошибок
            # self.statusHtml = None
            self.is_check = False
            self.result_code = ''
            # self.result = Result(description=self.DESCRIPTION)

        def get_class_name(self):
            return self.__class__.__name__

        def get_result(self):
            result = {
                'name': self.get_class_name(),
                'description': self.description,
                'info': list(self.info),
                'errors': self.errors,
                'result_code': self.result_code,
                'result_text': self.result_text,
                'status_html': StatusHTML.get_checker_status_html(self.result_code),
                'status_text': StatusHTML.get_checker_status_text(self.result_code),
            }
            return result

        def process(self):
            pass

        def get_result_status(self):
            if not self.info:
                self.result_code = 'good'
            else:
                res = set()
                for text_error in self.info:
                    res.add(self.STATUS_SET[text_error])
                if 'error' in res:
                    self.result_code = 'error'
                    return
                if 'reprimand' in res:
                    self.result_code = 'reprimand'
                    return
                if 'good' in res:
                    self.result_code = 'good'
                    return
                if 'disabled' in res:
                    self.result_code = 'disabled'

        # def set_checked(self):
        #     self.is_check = True
        #
        # def set_reprimand(self):
        #     self.result_text = self.REPRIMAND
        #
        # def set_all_good(self):
        #     self.result_text = self.GOOD
        #
        # def set_error(self):
        #     self.result_text = self.ERROR
        #
        # def set_none(self):
        #     self.result_text = self.NONE

    class Req(Check):
        DESCRIPTION = 'Реквизиты'

        INCORRECT_REQ = 'Есть некоректные'
        NO_REQS = 'Реквизиты отсутсвуют'

        STATUS_SET = {
            INCORRECT_REQ: 'reprimand',
            NO_REQS: 'reprimand',
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
                    self.errors.add(req)
                    self.info.add(self.INCORRECT_REQ)
            if len(self.errors) == len(reqs):  # если все реквизиты отсутствуют
                self.info = set()
                self.errors.clear()
                self.info.add(self.NO_REQS)
            # if not self.info:
            #     self.set_all_good()
            # else:
            #     # self.info = ','.join(errors)
            #     self.set_reprimand()

    class SaveComment(Check):
        """Поиск коментария от google chrome"""
        DESCRIPTION = 'Комметрарий от гугл хром'
        SAVED_FROM = '<!-- saved from'

        COMM_ON_PAGE = 'Комментарий saved from на странице'
        COMM_ON_PAGE_BLACK = 'Комментарий saved from на странице(black)'
        STATUS_SET = {
            COMM_ON_PAGE: 'reprimand',
            COMM_ON_PAGE_BLACK: 'good',
        }

        def process(self):
            self.find_comm()

        def find_comm(self):
            text = self.site.main.get_text()
            lines = text.split('\n')[:5]
            for line in lines:
                if self.SAVED_FROM in line:
                    if not self.site.cloac:
                        self.info.add(self.COMM_ON_PAGE)
                    else:
                        self.info.add(self.COMM_ON_PAGE_BLACK)
                    self.errors.add(self.SAVED_FROM)
                    break

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
            # if not self.info:
            #     self.set_reprimand()
            # else:
            #     self.set_all_good()

        def find_link(self):
            soup = self.site.main.get_soup()
            link = soup.find('a', href=self.POLICY_LINK)
            if not link:
                link = soup.find('a', href='/' + self.POLICY_LINK)
            if link:
                if self.LINK_TEXT not in link.text:
                    self.info.add(self.INCORRECT_TEXT)
            else:
                self.info.add(self.NO_LINK)

        def check_page(self):
            if not self.site.main.is_work():
                self.info.add(self.PAGE_NOT_WORK)

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
            self.check_page()
            self.check_form()
            self.find_redirect_url()
            # if self.info:
            #     self.set_reprimand()
            # else:
            #     self.set_all_good()

        def check_form(self):
            soup = self.site.main.get_soup()
            form = soup.find('form', action=self.ACTION)
            if not form:
                self.info.add(self.NO_SPAS_FORM)

        def check_page(self):
            # if self.site.spas.get_page_status_code() != 200:
            #     self.info.add(self.PAGE_NOT_WORK)
            if not self.site.spas.is_work():
                self.info.add(self.PAGE_NOT_WORK)

        def find_redirect_url(self):
            if self.FIND not in self.site.spas.get_text():
                self.info.add(self.INCORRECT_REDIRECT)

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
                self.info.add(self.PAGE_NOT_WORK)

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
            PIXEL_NOT_FOUND: 'disabled',
            ONE_NOT_CORRECT: 'error',
        }

        def process(self):
            self.find_pixel()

        def find_pixel(self):
            pixel_block = Page.find_text_block(self.site.success.get_text(),
                                               self.FBP_DESCRIPTION['start'], self.FBP_DESCRIPTION['end'])
            if pixel_block:
                fbp_1 = Page.find_text_block(pixel_block, self.FBP_1['start'], self.FBP_1['end'])
                fbp_2 = Page.find_text_block(pixel_block, self.FBP_2['start'], self.FBP_2['end'])
                if fbp_1 != fbp_2:
                    self.info.add(self.ONE_NOT_CORRECT)
                else:
                    self.result_text = fbp_1
            else:
                self.info.add(self.PIXEL_NOT_FOUND)

    class TtPixel(Check):
        DESCRIPTION = 'Пиклесль TikTok'
        TT = {'start': "ttq.load('",
              'end': "');"}

        PIXEL_NOT_FOUND = 'Пиксель не найден'

        STATUS_SET = {
            # PIXEL_NOT_FOUND: 'reprimand',
            PIXEL_NOT_FOUND: 'disabled',
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
                self.info.add(self.PIXEL_NOT_FOUND)
            else:
                self.result_text = tt_pixel

    class PageLink(Check):
        """Поиск некоректных внутрених ссылок"""
        DESCRIPTION = 'Внутрение сслыки'
        DO_NOT_CHECK = {'policy.html', 'terms.html',
                        '/policy.html', '/terms.html',
                        'spas.html'}

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
                            self.info.add(self.FIND_ALIEN)
                            self.errors.add(href)
                        else:
                            self.info.add(self.INCORRECT_INNER)
                            self.errors.add(href)
                except KeyError:
                    self.info.add(self.NO_HREF)

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
                self.info.add(self.NO_FORMS)

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
                    self.info.add(self.INCORRECT_ACTION)
                if form.name != 'name':
                    self.info.add(self.NAME_ERROR)
                if form.phone != 'phone':
                    self.info.add(self.PHONE_ERROR)
                if not form.phone_minlength:
                    self.info.add(self.NO_MIN_LEN)

    class ApiOrderTT(Check):
        """Проверка файла обработки заказа"""

        FLOW = '$data["flow"]'
        OFFER = '$data["offer"]'
        PRICE = '$data["base"]'
        COUNTRY = '$data["country"]'
        COMM = '$data["comm"]'

        # text errors info
        FILE_NOT_FOUND = 'Файл не найден в папке сайта'
        NO_OFFER = 'Оффер не найден'
        NO_FLOW = 'Поток не найден'
        NO_COUNTRY = 'Страна не найдена'
        NO_PRICE = 'Цена не найдена'
        NO_COMM = 'Комментарий не найден'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.file_lines = None
            self.price = None
            self.flow = None
            self.offer = None
            self.country = None
            self.comm = None

        def process(self):
            if Site.ORDER not in self.site.files:
                self.info.add(self.FILE_NOT_FOUND)
                return
            file_text = self.site.api_php.get_text()
            self.file_lines = file_text.split('\n')


        def find_params(self, param, func):
            pass

        def find_price(self):
            for line in self.file_lines:
                if self.PRICE in line:
                    self.find_price()
                    break

        def find_flow(self):
            for line in self.file_lines:
                if self.FLOW in line:
                    self.find_price()
                    break

        def find_offer(self):
            pass

        def find_country(self):
            pass

        def find_comm(self):
            pass



    # тело Главного чекера
    def __init__(self, site):
        self.site = site
        self.checkers = [
            self.SaveComment,
            self.OrderForms,
            self.PageLink,
            self.SpasPage,
            self.PolicyPage,
            self.TermsPage,
            self.SuccessPage,
            self.Req,
            self.FaceBookPixel,
            self.TtPixel,
        ]
        self.results_from_checkers = []
        self.result = set()

    def process(self):
        self.site.check_pages_conn()
        for check_class in self.checkers:
            checker = check_class(self.site)
            checker.process()
            checker.get_result_status()
            self.results_from_checkers.append(checker.get_result())
            self.result.add(checker.result_code)
        self.get_general_result()
        # print(self.result, 'general')

    def get_general_result(self):
        if 'error' in self.result:
            result_code = 'error'
        elif 'reprimand' in self.result:
            result_code = 'reprimand'
        elif 'good' in self.result:
            result_code = 'good'
        elif 'disabled' in self.result:
            result_code = 'disabled'
        else:
            result_code = 'none'
        dic = {
            'result_code': result_code,
            'result_html': StatusHTML.get_checker_status_html(result_code),
            'result_text': StatusHTML.get_checker_status_text(result_code),
        }
        self.result = dic


if __name__ == '__main__':
    site = Site(url='https://spaces-market.store/', is_cloac=True, dir_name='spaces-market.store/public_html')
    site.get_site_files()
    print(site.files)

    # main_ckecker = LinkChecker(site=site)
    # main_ckecker.process()
