import requests as req

# import beget_api_keys
from office.beget_api_keys import begget_login, begget_pass


class MyError(BaseException):
    def __init__(self, text='no text',**kwargs):
        self.text = text
        self.info = ', '.join(f'{k} - {v}' for k, v in kwargs.items()) if kwargs else ''
        self.no_connection = f'No connection: {self.info}'
        self.not_200_status = f'status code is: {self.info}'


class Connection:
    NO_CONN = 'No Connection'
    ENCODING = 'utf-8'

    def __init__(self, *args, **kwargs):
        self.response = None
        self.status_code = None

    def conn(self, url, method='get', **kwargs):
        print(url)
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
    sites = f'https://api.beget.com/api/site/getList?login={login}&passwd={password}&output_format=json'
    domains = f'https://api.beget.com/api/domain/getList?login={login}&passwd={password}&output_format=json'
    sub_domains = f'https://api.beget.com/api/domain/getSubdomainList?login={login}&passwd={password}&output_format=json'

    def get_sites(self):
        res = self.api_get(self.sites)
        if res['status'] == 'success':
            return res['answer']
        elif res['status'] == 'error':
            raise MyError(res['error_text'])

    def get_domains_list(self):
        res = self.api_get(self.domains)
        return res['answer']['result']

    def get_sub_domains_list(self):
        res = self.api_get(self.sub_domains)
        sub_domains = [sub_doms for sub_doms in res['answer']['result']]
        return sub_domains


if __name__ == '__main__':
    bm = Beget()
    print(bm.get_sites())
