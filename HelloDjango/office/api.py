import requests as req
from pprint import pprint
import json
if __name__ != '__main__':
    from . import models
    from office.beget_api_keys import begget_login, begget_pass
else:
    import beget_api_keys
    begget_login = beget_api_keys.begget_login
    begget_pass = beget_api_keys.begget_pass



class MyError(BaseException):
    NO_CONNECTION = 'No connection'
    def __init__(self, text='no text',**kwargs):
        self.text = text
        self.info = ', '.join(f'{k} - {v}' for k, v in kwargs.items()) if kwargs else ''
        self.no_connection = 'No connection'
        self.not_200_status = f'status code is: {self.info}'


class Connection:
    NO_CONN = 'No Connection'
    ENCODING = 'utf-8'

    def __init__(self, *args, **kwargs):
        self.response = None
        self.status_code = None

    def conn(self, url, method='get', **kwargs):
        try:
            if method == 'get':
                response = req.get(url)
            elif method == 'post':
                response = req.get(url, params=kwargs)
        except req.exceptions.ConnectionError:
            print(f'No connections: url={url}')
            raise MyError(f'No connections:', url=url)
        else:
            # print(response)
            response.encoding = Connection.ENCODING
            self.status_code = response.status_code
            self.response = response
            # if self.status_code != 200:
            #     raise MyError(f'status code {self.status_code}')


class ApiManager(Connection):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.api_status = None

    def api(self, url, method):
        self.conn(url, method=method)
        if self.status_code == 200:
            return self.response.json()
        else:
            return {'status': self.status_code}

    def api_get(self, url):
        return self.api(url, method='get')

    def api_post(self, url):
        return self.api(url, method='post')

    # def api_get(self, url):
    #     self.conn(url, method='get')
    #     if self.status_code == 200:
    #         return self.response.json()
    #     else:
    #         return self.status_code
    #
    # def api_post(self, url, **kwargs):
    #     self.conn(url, method='post', **kwargs)
    #     if self.status_code == 200:
    #         return self.response.json()
    #     else:
    #         return self.status_code


class Beget(ApiManager):
    # login = beget_api_keys.begget_login
    # password = beget_api_keys.begget_pass
    login = begget_login
    password = begget_pass
    # api
    BEGET_API_URL = 'https://api.beget.com/api/'
    sites_api = f'{BEGET_API_URL}site/getList?login={login}&passwd={password}&output_format=json'
    domains_api = f'{BEGET_API_URL}domain/getList?login={login}&passwd={password}&output_format=json'
    sub_domains_api = f'{BEGET_API_URL}domain/getSubdomainList?login={login}&passwd={password}&output_format=json'
    delite_site = f'{BEGET_API_URL}/site/delete?login={login}&passwd={password}&input_format=json&output_format=json&input_data='

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domains = []
        self.sub_domains = []
        self.sites = []

    def upload_sites(self):
        """Загрузсть сайты"""
        if not self.sites:

            res = self.api_get(self.sites_api)
            print(res)
            if res['status'] == 'success':
                for site in res['answer']['result']:
                    self.sites.append(site)


    def upload_domains_list(self):
        """Загрузсть домены"""
        if not self.domains:
            res = self.api_get(self.domains_api)
            if res['status'] == 'success':
                for domain in res['answer']['result']:
                    self.domains.append(domain)


    def upload_sub_domains_list(self):
        """Загрузсть поддомены"""
        if not self.sub_domains:
            res = self.api_get(self.sub_domains_api)
            if res['status'] == 'success':
                for sub_domain in res['answer']['result']:
                    self.sub_domains.append(sub_domain)

    def get_sites(self):
        """Получить список сайтов"""
        if not self.sites:
            self.upload_sites()
        return self.sites

    def get_domains(self):
        """Получить список доменов"""
        if not self.domains:
            self.upload_domains_list()
        return self.domains

    def get_sub_domains(self):
        """Получить список поддоменов"""
        if not self.sub_domains:
            self.upload_sub_domains_list()
        return self.sub_domains

    def get_all_domains(self):
        """Получить список всех доменов"""
        if not self.domains:
            self.upload_domains_list()
        if not self.sub_domains:
            self.upload_sub_domains_list()

        return self.domains + self.sub_domains

    def update_domains(self):
        """Обновить список доменов"""
        # # TODO - перенести в Domain?
        # all_domains_list = self.get_all_domains()
        # beget_doms_id = [dom['id'] for dom in all_domains_list]
        # db_doms_id = [dom.beget_id for dom in models.Domain.objects.all()]
        # to_del = set(db_doms_id) - set(beget_doms_id)
        # to_add = set(beget_doms_id) - set(db_doms_id)
        # for dom_id in to_del:
        #     dom = models.Domain.objects.get(beget_id=dom_id)
        #     dom.delete()
        # for domain in all_domains_list:
        #     dom_id = domain['id']
        #     if dom_id in to_add:
        #         name = domain['fqdn']
        #         dom = models.Domain(name=name, beget_id=dom_id)
        #         dom.save()
        all_root_domains_list = self.get_domains()
        beget_doms_id = [dom['id'] for dom in all_root_domains_list]
        db_doms_id = [dom.beget_id for dom in models.RootDomain.objects.all()]
        to_del = set(db_doms_id) - set(beget_doms_id)
        to_add = set(beget_doms_id) - set(db_doms_id)
        for dom_id in to_del:
            dom = models.RootDomain.objects.get(beget_id=dom_id)
            dom.delete()
        for domain in all_root_domains_list:
            dom_id = domain['id']
            if dom_id in to_add:
                name = domain['fqdn']
                dom = models.RootDomain(name=name, beget_id=dom_id)
                dom.save()

        all_sub_domains_list = self.get_sub_domains()
        beget_doms_id = [dom['id'] for dom in all_sub_domains_list]
        db_doms_id = [dom.beget_id for dom in models.SubDomain.objects.all()]
        to_del = set(db_doms_id) - set(beget_doms_id)
        to_add = set(beget_doms_id) - set(db_doms_id)
        for dom_id in to_del:
            dom = models.SubDomain.objects.get(beget_id=dom_id)
            dom.delete()
        for domain in all_sub_domains_list:
            dom_id = domain['id']
            if dom_id in to_add:
                name = domain['fqdn']
                root_dom = models.RootDomain.objects.get(beget_id=domain['domain_id'])
                dom = models.SubDomain(name=name, beget_id=dom_id, root_domain=root_dom)
                dom.save()

    def del_site(self,beget_id):
        """Удаление сайта с бегета"""
        url = self.delite_site + json.dumps({'id': beget_id})
        res = self.api(url, 'get')
        if res['status'] == 'success':
            return True
        return False







if __name__ == '__main__':
    bm = Beget()
    pprint(bm.get_sub_domains())