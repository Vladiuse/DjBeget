from bs4 import BeautifulSoup

from .api import Connection


class Url:
    SUCCESS_PAGE = 'success/success.html'
    POLICY = 'policy.html'
    SPAS = 'spas.html'

    def __init__(self, url, **kwargs):
        self.url = url + '' if url.endswith('/') else '/'
        self.success_url = self.url + Url.SUCCESS_PAGE
        self.policy_url = self.url + Url.POLICY
        self.spas_url = self.url + Url.SPAS

    def get_url(self):
        return self.url

    def get_success_url(self):
        return self.success_url

    def get_policy_url(self):
        return self.policy_url

    def get_spas_url(self):
        return self.spas_url


class Checker(Connection):

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

    def process(self):
        pass

    def get_result(self):
        return self.result

    @staticmethod
    def find_text_block(text, start, end):
        start_pos = text.find(start)
        end_pos = text.find(end)
        if start_pos != -1 and end_pos != -1:
            return text[start_pos + len(start):end_pos]


class MainPage(Checker):
    """
    Обработчик главной страницы
    """
    REQUISITES = ['ИП Гребенщиков', 'УНП 19345252', 'Радиальная']

    #INFO
    REQUISITES_IN_PAGE = 'Присутствуют'
    REQUISITES_ERROR = 'Не коректные реквизиты'

    def check_requisites(self):
        req_res = all(req in self.soup.text for req in MainPage.REQUISITES)
        req_res = MainPage.REQUISITES_IN_PAGE if req_res else MainPage.REQUISITES_ERROR
        self.result.update({'requisites': req_res})

    def process(self):
        self.make_soup()
        self.check_requisites()


class SpasPage(Checker):
    """
    Обработчик страницы отзыва
    """


class PolicyPage(Checker):
    """
    Обработчик policy page
    """


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
        Поикс пикселя на странице
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
            self.result.update({'pixel': SuccessPage.correct_pixel})
        else:
            self.result.update({'pixel': self.pixel_in_land})


class LinkCheckerManager:

    def __init__(self, url, **kwargs):
        self.url_class = Url(url=url)
        self.main_page = MainPage(url=self.url_class.get_url(), )
        self.policy_page = PolicyPage(url=self.url_class.get_policy_url())
        self.success_page = SuccessPage(url=self.url_class.get_success_url(), **kwargs)
        self.result = {}

    def process(self):
        self.main_page.process()
        self.success_page.process()
        self.collect_results()

    def collect_results(self):
        for item in self.main_page, self.policy_page, self.success_page:
            self.result.update(item.get_result())

