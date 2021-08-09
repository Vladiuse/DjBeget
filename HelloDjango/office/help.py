import requests
LOCAL_HOST = '127.0.0.1:8000'


class ImagePrev:
    def __init__(self, url, name, host):
        self.host = host
        self.base = 'https://render-tron.appspot.com/screenshot/'
        self.path_local = 'office/static/office/img/old_lands/'   # local
        self.path = '/home/v/vladiuse/django/public_html/static/office/img/old_lands/'
        self.url = url
        self.name = name

    def get_image(self, url=1):
        # path = 'office/static/office/img/old_lands/test.jpg'
        if self.host in LOCAL_HOST:
            path = self.path_local + self.name + '.jpg'
        else:
            path = self.path + self.name + '.jpg'
        # url = 'http://vladiuse.beget.tech/kupal/'
        response = requests.get(self.base + self.url, stream=True)
        # save file, see https://stackoverflow.com/a/13137873/7665691
        if response.status_code == 200:
            with open(path, 'wb') as file:
                for chunk in response:
                    file.write(chunk)
        if self.host in LOCAL_HOST:
            static_path = path.replace('office/static/', '') # local
        else:
            static_path = path.replace('/home/v/vladiuse/django/public_html/static/', '')
        return static_path



def get_url_link_from_name(domain_name):
    protokol = 'https'
    if 'beget' in domain_name:
        protokol = 'http'
    return protokol + '://' + domain_name + '/'

# x = ImagePrev()
# res = x.get_image()
# print(res)
# BASE = 'https://render-tron.appspot.com/screenshot/'
#
# url = 'https://google.com'
# url = 'http://vladiuse.beget.tech/kupal/'
# path = 'target.jpg'
# print(BASE + url)
# response = requests.get(BASE + url, stream=True)
# # save file, see https://stackoverflow.com/a/13137873/7665691
# if response.status_code == 200:
#     with open(path, 'wb') as file:
#         for chunk in response:
#             print(chunk)
#             file.write(chunk)