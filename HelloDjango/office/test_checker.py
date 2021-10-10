import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from new_checker import LinkChecker, Page, Site, PageFile


class TestReq(unittest.TestCase):
    """Тест проверки реквизитов"""

    def setUp(self):
        self.site = Site('1')
        self.reqALL = '<p>ИПГребенщиков,УНП19345252</p>' \
                      '<p>г.Минск,ул.Радиальная,д.40</p>' \
                      '<p>E-mail:zenitcotrade@gmail.com</p>' \
                      '<p>Телефон:+375(29)140-29-00</p>'

        self.req_no_name = '<p>,УНП19345252</p>' \
                           '<p>г.Минск,ул.Радиальная,д.40</p>' \
                           '<p>E-mail:zenitcotrade@gmail.com</p>' \
                           '<p>Телефон:+375(29)140-29-00</p>'

        self.req_no_name_phone = '<p>,УНП19345252</p>' \
                                 '<p>г.Минск,ул.Радиальная,д.40</p>' \
                                 '<p>E-mail:zenitcotrade@gmail.com</p>' \
                                 '<p>Телефон:+375'
        self.req_no_all = 'ifninieqvneqv'

    def test_no_req(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value='123'):
            req = LinkChecker.Req(self.site)
            req.process()
            self.assertTrue(req.NO_REQS in req.info)

    def test_fb_In(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value=self.reqALL):
            req = LinkChecker.Req(self.site)
            req.find_req_fb()
            req.get_result_status()
            self.assertEqual(req.result_code, 'good')

    def test_fb_no_name(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value=self.req_no_name):
            req = LinkChecker.Req(self.site)
            req.find_req_fb()
            self.assertTrue('name' in req.errors)

    def test_tt_no_name_phone(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value=self.req_no_name_phone):
            req = LinkChecker.Req(self.site)
            req.find_req_tt()
            self.assertTrue('name' in req.errors and 'phone' in req.errors)

    def test_no_reqs(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value=self.req_no_all):
            req = LinkChecker.Req(self.site)
            req.find_req_tt()
            self.assertEqual(len(req.errors), 0)
            self.assertTrue(req.NO_REQS in req.info and len(req.info) == 1)


class FindCommTest(unittest.TestCase):

    def setUp(self):
        self.site = Site('no url')
        self.NO_COMM = ''
        self.COMM_IN = 'iweernb2bmo2mo2-\n<!-- saved from\nwqmfqwofqw'

    def test_comm_on_page(self):
        with patch.object(Page, 'get_text', return_value=self.COMM_IN):
            save = LinkChecker.SaveComment(self.site)
            save.process()
            self.assertTrue(save.COMM_ON_PAGE in save.info)

    def test_comm_not_page(self):
        with patch.object(Page, 'get_text', return_value=self.NO_COMM):
            save = LinkChecker.SaveComment(self.site)
            save.process()
            self.assertFalse(save.info)

    def test_cloac_comm(self):
        """коментарий на заклоаченой странице"""
        self.site.cloac = True
        with patch.object(Page, 'get_text', return_value=self.COMM_IN):
            save = LinkChecker.SaveComment(self.site)
            save.process()
            self.assertTrue(save.COMM_ON_PAGE_BLACK in save.info)


class PolicyTest(unittest.TestCase):

    def setUp(self):
        self.site = Site('no url')
        self.site.main.status_code = 200
        self.LINK_CORRECT = '<p class="conf-link doclinks">' \
                            '<a class="nav-link" href="policy.html">Политика конфиденциальности </a></p>'
        self.INCORRECT_HREF = '<p class="conf-link doclinks">' \
                              '<a class="nav-link" href="policy1.html">Политика конфиденциальности </a></p>'
        self.NO_TEXT = '<p class="conf-link doclinks">' \
                       '<a class="nav-link" href="policy.html">Политика конxxxxфиденциальности </a></p>'
        self.SLASH_LINK = '<p class="conf-link doclinks">' \
                          '<a class="nav-link" href="/policy.html">Политика конфиденциальности </a></p>'

    def test_all_good(self):
        soup = BeautifulSoup(self.LINK_CORRECT, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.PolicyPage(self.site)
            checker.process()
            self.assertFalse(checker.info)

    def test_all_good_slash(self):
        soup = BeautifulSoup(self.SLASH_LINK, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.PolicyPage(self.site)
            checker.process()
            self.assertFalse(checker.info)

    def test_no_href(self):
        soup = BeautifulSoup(self.INCORRECT_HREF, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.PolicyPage(self.site)
            checker.process()
            self.assertTrue(checker.NO_LINK in checker.info)

    def test_no_link_text(self):
        soup = BeautifulSoup(self.NO_TEXT, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.PolicyPage(self.site)
            checker.process()
            self.assertTrue(checker.INCORRECT_TEXT in checker.info)

    def test_no_conn(self):
        soup = BeautifulSoup(self.LINK_CORRECT, 'lxml')
        self.site.main.status_code = 404
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.PolicyPage(self.site)
            checker.process()
            self.assertTrue(checker.PAGE_NOT_WORK in checker.info)


class TermsTest(unittest.TestCase):

    def setUp(self):
        self.site = Site('no url')
        self.site.main.status_code = 200
        self.LINK_CORRECT = '<p class="conf-link doclinks">' \
                            '<a class="nav-link" href="terms.html">Пользовательское соглашение </a></p>'
        self.INCORRECT_HREF = '<p class="conf-link doclinks">' \
                              '<a class="nav-link" href="policy1.html">Пользовательское соглашение </a></p>'
        self.NO_TEXT = '<p class="conf-link doclinks">' \
                       '<a class="nav-link" href="terms.html">Пользоватxxxxxxxельское соглашение </a></p>'

        self.LINK_CORRECT_SLASH = '<p class="conf-link doclinks">' \
                                  '<a class="nav-link" href="terms.html">Пользовательское соглашение </a></p>'

    def test_all_good(self):
        soup = BeautifulSoup(self.LINK_CORRECT, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.TermsPage(self.site)
            checker.process()
            self.assertFalse(checker.info)

    def test_all_good_slash(self):
        soup = BeautifulSoup(self.LINK_CORRECT_SLASH, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.TermsPage(self.site)
            checker.process()
            self.assertFalse(checker.info)

    def test_no_href(self):
        soup = BeautifulSoup(self.INCORRECT_HREF, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.TermsPage(self.site)
            checker.process()
            self.assertTrue(checker.NO_LINK in checker.info)

    def test_no_link_text(self):
        soup = BeautifulSoup(self.NO_TEXT, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.TermsPage(self.site)
            checker.process()
            self.assertTrue(checker.INCORRECT_TEXT in checker.info)

    def test_no_conn(self):
        soup = BeautifulSoup(self.LINK_CORRECT, 'lxml')
        self.site.main.status_code = 404
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.TermsPage(self.site)
            checker.process()
            self.assertTrue(checker.PAGE_NOT_WORK in checker.info)


class SpasPageTest(unittest.TestCase):
    # TODO дописать тесты на удачное завершение

    def setUp(self):
        self.site = Site('1')
        self.spas = LinkChecker.SpasPage(self.site)
        # self.site.spas.status_code = 200

    def test_form_find(self):
        html = ' <form class="form" action="spas.html" method="post" id="register"></form>'
        soup = BeautifulSoup(html, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.spas.check_form()
            self.assertEqual(self.spas.info, set())

    def test_no_redirect(self):
        self.site.spas.status_code = 200
        with patch.object(Page, 'get_text', return_value='123'):
            self.spas.find_redirect_url()
            self.assertTrue(self.spas.INCORRECT_REDIRECT in self.spas.info)

    def test_no_form(self):
        soup = BeautifulSoup('123', 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.spas.check_form()
            self.assertTrue(self.spas.NO_SPAS_FORM in self.spas.info)

    def test_page_not_work(self):
        self.site.spas.status_code = 404
        self.spas.check_page()
        self.assertTrue(self.spas.PAGE_NOT_WORK in self.spas.info)


class FbPixelText(unittest.TestCase):

    def setUp(self):
        self.site = Site('1')
        self.fb = LinkChecker.FaceBookPixel(self.site)

    def test_pixel_find(self):
        pixel = """<!-- Facebook Pixel Code -->fbq('init', '379588770181368');\n
        <noscript><img height="1" width="1" style="display:none" 
        src="https://www.facebook.com/tr?id=379588770181368&ev=PageView&noscript=1"/></noscript>
        <!-- End Facebook Pixel Code -->"""
        with patch.object(Page, 'get_text', return_value=pixel):
            self.fb.process()
            self.assertEqual(self.fb.result_value['pixel'], '379588770181368')

    def test_different_pixels(self):
        pixel = """<!-- Facebook Pixel Code -->fbq('init', '379588770181368');\n
                <noscript><img height="1" width="1" style="display:none" 
                src="https://www.facebook.com/tr?id=379588770181300&ev=PageView&noscript=1"/></noscript>
                <!-- End Facebook Pixel Code -->"""
        with patch.object(Page, 'get_text', return_value=pixel):
            self.fb.process()
            self.assertTrue(self.fb.ONE_NOT_CORRECT in self.fb.info)

    def test_pixel_block_not_found(self):
        pixel = """<!-- Facebook1111 Pixel Code -->fbq('init', '379588770181368');\n
                <noscript><img height="1" width="1" style="display:none" 
                src="https://www.facebook.com/tr?id=379588770181300&ev=PageView&noscript=1"/></noscript>
                <!-- End Facebook Pixel Code111 -->"""
        with patch.object(Page, 'get_text', return_value=pixel):
            self.fb.process()
            self.assertTrue(self.fb.PIXEL_NOT_FOUND in self.fb.info)


class TtPixelText(unittest.TestCase):

    def setUp(self):
        self.site = Site('1')
        self.tt = LinkChecker.TtPixel(self.site)

    def test_pixel_found(self):
        # pixel = " xx  xx ttq.load('C4TM1C7PECQ6U88FAJ20'); xx "
        pixel = "ttq.load('C59GNENGE0M9N03GTOE0');"
        with patch.object(Page, 'get_text', return_value=pixel):
            self.tt.process()
            self.assertEqual(self.tt.result_value['pixel'], 'C59GNENGE0M9N03GTOE0')

    def test_not_pixel_found(self):
        pixel = " xx  xx ttq.loadxx('C4TM1C7PECQ6U88FAJ20'); xx "
        with patch.object(Page, 'get_text', return_value=pixel):
            self.tt.process()
            self.assertTrue(self.tt.PIXEL_NOT_FOUND in self.tt.info)


class LinksTest(unittest.TestCase):

    def setUp(self):
        self.site = Site('1')
        self.link_check = LinkChecker.PageLink(self.site)

    def test_all_good(self):
        text = '<a href="spas.html" class="button-m">Оставить отзыв</a>' \
               '<a href="policy.html" class="button-m">Оставить отзыв</a>' \
               '<a href="/policy.html" class="button-m">Оставить отзыв</a>' \
               '<a href="terms.html" class="button-m">Оставить отзыв</a>' \
               '<a href="/terms.html" class="button-m">Оставить отзыв</a>' \
               '<a href="spas.html" class="button-m">Оставить отзыв</a>' \
               '<a href="#order" class="button-m">Оставить отзыв</a>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.link_check.process()
            self.assertTrue(len(self.link_check.info) == 0)

    def test_alien_http(self):
        text = '<a href="http://spas.html" class="button-m">Оставить отзыв</a>' \
               '<a href="https://policy.html" class="button-m">Оставить отзыв</a>' \
               '<a href="spas.html" class="button-m">Оставить отзыв</a>' \
               '<a href="#order" class="button-m">Оставить отзыв</a>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.link_check.process()
            self.assertTrue(self.link_check.FIND_ALIEN in self.link_check.info)
            self.assertTrue('http://spas.html' in self.link_check.errors)

    def test_incorrect(self):
        text = '<a href="123#spas.html" class="button-m">Оставить отзыв</a>' \
               '<a href="pp#policy.html" class="button-m">Оставить отзыв</a>' \
               '<a href="spas.html" class="button-m">Оставить отзыв</a>' \
               '<a href="#order" class="button-m">Оставить отзыв</a>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.link_check.process()
            self.assertTrue(self.link_check.INCORRECT_INNER in self.link_check.info)
            self.assertTrue('pp#policy.html' in self.link_check.errors)

    def test_no_href(self):
        text = '<a href="" class="button-m">Оставить отзыв</a>' \
               '<a href="pp#policy.html" class="button-m">Оставить отзыв</a>' \
               '<a href="spas.html" class="button-m">Оставить отзыв</a>' \
               '<a href="#order" class="button-m">Оставить отзыв</a>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.link_check.process()
            self.assertTrue(self.link_check.INCORRECT_INNER in self.link_check.info)


class HTMLFormTest(unittest.TestCase):

    def setUp(self):
        text = '<form action="good.php">' \
               '<input type="text" name="name">' \
               '<input type="text" name="phone" minlength="111">' \
               '</form>'
        soup = BeautifulSoup(text, 'lxml')
        form_soup_work = soup.find('form')
        self.form = LinkChecker.HTMLForm(form_soup=form_soup_work)

    def test_get_action(self):
        self.form.find_action()
        self.assertEqual(self.form.action, 'good.php')

    def test_get_name(self):
        self.form.find_name()
        self.assertEqual(self.form.name, 'name')

    def test_get_phone(self):
        self.form.find_phone()
        self.assertEqual(self.form.phone, 'phone')

    def test_min_length(self):
        self.form.find_phone()
        self.form.get_phone_minlength()
        self.assertEqual(self.form.phone_minlength, '111')


class OrderFormsTest(unittest.TestCase):

    def setUp(self):
        self.site = Site('1')
        self.forms = LinkChecker.OrderForms(self.site)

    def test_all_good(self):
        text = '<form action="api.php">' \
               '<input type="text" name="name">' \
               '<input type="text" name="phone" minlength="9">' \
               '</form>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.forms.process()
            self.assertEqual(self.forms.info, set())

    def test_no_phone(self):
        text = '<form action="api.php">' \
               '<input type="text" name="name">' \
               '<input type="text" name="phone1" minlength="9">' \
               '</form>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.forms.process()
            self.assertTrue(self.forms.PHONE_ERROR in self.forms.info)

    def test_no_name(self):
        text = '<form action="api.php">' \
               '<input type="text" name="xxxx">' \
               '<input type="text" name="phone" minlength="9">' \
               '</form>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.forms.process()
            self.assertTrue(self.forms.NAME_ERROR in self.forms.info)

    def test_no_minlenght(self):
        text = '<form action="api.php">' \
               '<input type="text" name="name">' \
               '<input type="text" name="phone" minlength="">' \
               '</form>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.forms.process()
            self.assertTrue(self.forms.NO_MIN_LEN in self.forms.info)

    def test_no_forms(self):
        text = '<form action="spas.html">' \
               '<input type="text" name="xxxx">' \
               '<input type="text" name="phone" minlength="9">' \
               '</form>'
        soup = BeautifulSoup(text, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.forms.process()
            self.assertTrue(self.forms.NO_FORMS in self.forms.info)


class CheckTest(unittest.TestCase):

    def setUp(self):
        site = Site('1')
        self.checker = LinkChecker.Check(site)
        self.checker.STATUS_SET.update({'error_1': 'error', 'error_2': 'reprimand'})

    def test_all_good(self):
        self.checker.get_result_status()
        self.assertEqual(self.checker.result_code, 'good')

    def test_error_status(self):
        self.checker.info.add('error_1')
        self.checker.info.add('error_2')
        self.checker.get_result_status()
        self.assertEqual(self.checker.result_code, 'error')

    def test_rep_status(self):
        self.checker.info.add('error_2')
        self.checker.get_result_status()
        self.assertEqual(self.checker.result_code, 'reprimand')


class PageFileTest(unittest.TestCase):
    """тест функции поиска значения переменных(php)"""

    def test_find_variable(self):
        line = """$data["country"] = 'pl';\n"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, 'pl')

    def test_find_variable_double_bracket(self):
        line = """$data["country"] = "123some-text";\n"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, '123some-text')

    def test_find_variable_no_equal(self):
        line = """$data["country"]  'pl';\n"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, None)

    def test_find_variable_int(self):
        line = """$data["country"] = "123"; // some text\n"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, '123')

    def test_find_variable_float(self):
        line = """$data["country"] = "123.123";\n"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, '123.123')

    def test_find_variable_no_end_php(self):
        line = """$data["country"] = "123.123"\n"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, '123.123')

    def test_find_variable_no_end_line(self):
        line = """$data["country"] = '123.123'"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, '123.123')

    def test_find_variable_no_value_str(self):
        line = """$data["country"] = ''"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, '')

    def test_find_variable_variable(self):
        # TODO - хз че делать с этим
        line = """$data["country"] = POST"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, 'POST')

    def test_php_comm_in_line(self):
        # TODO - дописать для других коментрариев
        line = """$data["country"] = 123 //some text"""
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, '123')

    def test_some(self):
        line = "$CLOAKING['ALLOW_GEO'] = 'BY,PL'"
        result = PageFile.get_variable_value(line)
        self.assertEqual(result, 'BY,PL')

class ApiOrderTTTest(unittest.TestCase):

    def setUp(self):
        self.site = Site('1', dir_name='some_name')
        self.site.files.add(Site.ORDER)
        self.checker = LinkChecker.ApiOrderTT(site=self.site)

    def test_file_not_found(self):
        self.site.files.clear()
        self.checker.process()
        self.assertEqual(self.checker.info, {self.checker.FILE_NOT_FOUND})

    def test_all_good(self):
        file_text = """$data["base"] = "55euro";\n
                    $data["country"] = 'pl';\n
                    $data["offer"] = 25;\n
                    $data["comm"] = 'комментарий';\n
                    $data["flow"] = 90;\n"""
        file_text = file_text.split('\n')
        with patch.object(PageFile, 'get_file_lines', return_value=file_text):
            self.checker.find_variables_value()
            self.checker.add_errors()
            self.assertEqual(self.checker.result_value['base'], '55euro')
            self.assertEqual(self.checker.result_value['country'], 'pl')
            self.assertEqual(self.checker.result_value['offer'], '25')
            self.assertEqual(self.checker.result_value['comm'], 'комментарий')
            self.assertEqual(self.checker.result_value['flow'], '90')
            self.assertEqual(self.checker.info, set())

    def test_offer_not_found(self):
        file_text = """$data["base"] = "55euro";\n
                    $data["country"] = 'pl';\n
                    $data["offer"] = ;\n
                    $data["comm"] = 'комментарий';\n
                    $data["flow"] = 90;\n"""
        file_text = file_text.split('\n')
        with patch.object(PageFile, 'get_file_lines', return_value=file_text):
            self.checker.process()
            self.assertTrue(self.checker.NO_OFFER in self.checker.info)
            self.assertTrue(len(self.checker.info) == 1)

    def test_comm_flow_not_found(self):
        file_text = """$data["base"] = "55euro";\n
                    $data["country"] = 'pl';\n
                    $data["offer"] = 1;\n
                    $data["comm"] = '';\n
                    $data["flow"] = ;\n"""
        file_text = file_text.split('\n')
        with patch.object(PageFile, 'get_file_lines', return_value=file_text):
            self.checker.process()
            self.assertTrue(self.checker.NO_FLOW in self.checker.info)
            self.assertTrue(self.checker.NO_COMM in self.checker.info)
            self.assertTrue(len(self.checker.info) == 2)


class HideClickTest(unittest.TestCase):

    def setUp(self):
        self.site = Site('1', dir_name='some_name', is_cloac=True)
        self.site.files.add(Site.CLOAC_FILE)
        self.checker = LinkChecker.HideClick(site=self.site)

    def test_disable_checker(self):
        self.site = Site('1', dir_name='some_name')
        self.checker = LinkChecker.HideClick(site=self.site)
        with patch.object(PageFile, 'get_file_lines', count=20,return_value=['123']):
            self.checker.process()
            self.assertTrue(self.checker.CLO_NOT_ACTIVE in self.checker.info)
            self.assertTrue(len(self.checker.info) == 1)

    def test_file_not_found(self):
        """Файл клоаки не найден"""
        self.site.files.clear()
        with patch.object(PageFile, 'get_file_lines', count=20, return_value=['123']):
            self.checker.process()
            self.assertTrue(self.checker.FILE_NOT_FOUND in self.checker.info)
            self.assertTrue(len(self.checker.info) == 1)

    def test_all_good(self):
        text = """/* Required settings     */
                $CLOAKING['WHITE_PAGE'] = 'white.html';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off';// replace \n
                $CLOAKING['STEALTH'] = 'off';// replace\n
                /*********************************************/\n
                /* Available additional settings  */\n
                /* Geo filter: Displ.  */\n
                /* For example, if you enter 'RU,UA' inrs froraine */\n
                $CLOAKING['ALLOW_GEO'] = 'BY,PL';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines', count=20,return_value=text):
            self.checker.process()
            self.assertEqual(self.checker.result_value['black'], 'black.html')
            self.assertEqual(self.checker.result_value['white'], 'white.html')
            self.assertEqual(self.checker.result_value['geo'], 'BY,PL')
            self.assertEqual(self.checker.result_value['debug'], 'off')

    def test_no_white_variable(self):
        text = """/* Required settings     */
                $CLOAKING['WHITE_PAGE'] = '';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'BY,PL';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines', count=20,return_value=text):
            self.checker.find_variables_value()
            self.checker.add_errors()
            self.assertTrue(self.checker.NO_WHITE in self.checker.info)

    def test_no_black_variable(self):
        text = """/* Required settings     */\n
                $CLOAKING['WHITE_PAGE'] = 'www';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = '';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'BY,PL';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines', count=20,return_value=text):
            self.checker.find_variables_value()
            self.checker.add_errors()
            self.assertTrue(self.checker.NO_BLACK in self.checker.info)


    def test_incorrect_black(self):
        text = """/* Required settings     */
                $CLOAKING['WHITE_PAGE'] = 'white.html';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black1.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'BY,PL';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines', count=20,return_value=text):
            self.checker.find_variables_value()
            self.checker.check_black_name()
            self.assertTrue(self.checker.BLACK_INCORRECT in self.checker.info)
            self.assertTrue(self.checker.errors == {'black1.html'})

    def test_incorrect_debug(self):
        text = """/* Required settings     */
                $CLOAKING['WHITE_PAGE'] = 'white.html';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off1';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'BY,PL';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines',count=20, return_value=text):
            self.checker.find_variables_value()
            self.checker.check_debug_mode()
            self.assertTrue(self.checker.DEBUG_INCORRECT in self.checker.info)
            self.assertTrue(self.checker.errors == {'off1'})

    def test_debug_ON(self):
        text = """/* Required settings     */
                $CLOAKING['WHITE_PAGE'] = 'white.html';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'on';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'BY,PL';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines', count=20,return_value=text):
            self.checker.find_variables_value()
            self.checker.check_debug_mode()
            self.assertTrue(self.checker.DEBUG_MODE_ON in self.checker.info)

    def test_incorrect_white(self):
        text = """/* Required settings     */
                $CLOAKING['WHITE_PAGE'] = 'whiteX.html';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'BY,PL';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines', count=20,return_value=text):
            self.checker.find_variables_value()
            self.checker.check_white_name()
            self.assertTrue(self.checker.WHITE_INCORRECT in self.checker.info)
            self.assertTrue(self.checker.errors == {'whiteX.html'})

    def test_incorrect_geo_len(self):
        text = """/* Required settings     */\n
                $CLOAKING['WHITE_PAGE'] = 'white.html';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'BYY,PLL';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines',count=20, return_value=text):
            self.checker.find_variables_value()
            self.checker.check_geo()
            self.assertTrue(self.checker.GEO_LEN_ERROR in self.checker.info)
            self.assertTrue(self.checker.errors == {'byy', 'pll'})

    def test_incorrect_char_geo(self):
        text = """/* Required settings     */
                $CLOAKING['WHITE_PAGE'] = 'white.html';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'BY1,PL*';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines',count=20, return_value=text):
            self.checker.find_variables_value()
            self.checker.check_geo()
            self.assertTrue(self.checker.GEO_LEN_ERROR in self.checker.info)
            self.assertTrue(self.checker.errors == {'by1', 'pl*'})

    def test_incorrect_geo(self):
        text = """/* Required settings     */
                $CLOAKING['WHITE_PAGE'] = 'white.html';//PHP/\n
                $CLOAKING['OFFER_PAGE'] = 'black.html';//PHP/H\n
                $CLOAKING['DEBUG_MODE'] = 'off';// replace \n
                $CLOAKING['ALLOW_GEO'] = 'XX,AA';"""
        text = text.split('\n')
        with patch.object(PageFile, 'get_file_lines', count=20,return_value=text):
            self.checker.find_variables_value()
            self.checker.check_geo()
            self.assertTrue(self.checker.GEO_INCORRECT_NAME in self.checker.info)
            self.assertTrue(self.checker.errors == {'aa', 'xx'})


if __name__ == '__main__':
    unittest.main()
