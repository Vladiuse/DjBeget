import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from new_checker import LinkChecker, Page, Site


class Test:

    def __init__(self):
        self.text = 'find'

    def get_text(self):
        return self.text


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

    def test_no_req(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value='123'):
            req = LinkChecker.Req(self.site)
            req.process()
            self.assertEqual(req.result_text, req.REPRIMAND)

    def test_fb_In(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value=self.reqALL):
            req = LinkChecker.Req(self.site)
            req.find_req_fb()
            self.assertEqual(req.result_text, req.GOOD)

    def test_fb_no_name(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value=self.req_no_name):
            req = LinkChecker.Req(self.site)
            req.find_req_fb()
            self.assertEqual(req.info, ['name'])

    def test_tt_no_name_phone(self):
        with patch.object(Page, 'get_text_no_spaces_soup', return_value=self.req_no_name_phone):
            req = LinkChecker.Req(self.site)
            req.find_req_tt()
            self.assertEqual(req.info, ['name', 'phone'])


class FindCommTest(unittest.TestCase):

    def setUp(self):
        self.site = Site('no url')
        self.NO_COMM = ''
        self.COMM_IN = 'iweernb2bmo2mo2-\n<!-- saved from\nwqmfqwofqw'

    def test_comm_on_page(self):
        with patch.object(Page, 'get_text', return_value=self.COMM_IN):
            save = LinkChecker.SaveComment(self.site)
            save.process()
            self.assertEqual(save.result_text, save.REPRIMAND)

    def test_comm_not_page(self):
        with patch.object(Page, 'get_text', return_value=self.NO_COMM):
            save = LinkChecker.SaveComment(self.site)
            save.process()
            self.assertEqual(save.result_text, save.GOOD)


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

    def test_all_good(self):
        soup = BeautifulSoup(self.LINK_CORRECT, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.PolicyPage(self.site)
            checker.process()
            self.assertTrue(checker.result_text, checker.GOOD)

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

    def test_all_good(self):
        soup = BeautifulSoup(self.LINK_CORRECT, 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            checker = LinkChecker.TermsPage(self.site)
            checker.process()
            self.assertTrue(checker.result_text, checker.GOOD)

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
        self.site.spas.status_code = 200

    def test_no_redirect(self):
        with patch.object(Page, 'get_text', return_value='123'):
            self.spas.find_redirect_url()
            self.assertTrue(self.spas.INCORRECT_REDIRECT in self.spas.info)

    def test_no_form(self):
        soup = BeautifulSoup('123', 'lxml')
        with patch.object(Page, 'get_soup', return_value=soup):
            self.spas.check_form()
            self.assertTrue(self.spas.NO_SPAS_FORM in self.spas.info)


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
            self.assertEqual(self.fb.result_text, '379588770181368')

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
        pixel = " xx  xx ttq.load('C4TM1C7PECQ6U88FAJ20'); xx "
        with patch.object(Page, 'get_text', return_value=pixel):
            self.tt.process()
            self.assertEqual(self.tt.result_text, 'C4TM1C7PECQ6U88FAJ20')

    def test_not_pixel_found(self):
        pixel = " xx  xx ttq.loadxx('C4TM1C7PECQ6U88FAJ20'); xx "
        with patch.object(Page, 'get_text', return_value=pixel):
            self.tt.process()
            self.assertTrue(self.tt.PIXEL_NOT_FOUND in self.tt.info)


if __name__ == '__main__':
    unittest.main()
