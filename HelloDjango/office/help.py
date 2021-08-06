import requests


class ImagePrev:
    def __init__(self, url, name):
        self.base = 'https://render-tron.appspot.com/screenshot/'
        self.path = 'office/static/office/img/old_lands/'
        self.url = url
        self.name = name

    def get_image(self, url=1):
        # path = 'office/static/office/img/old_lands/test.jpg'
        path = self.path + self.name + '.jpg'
        # url = 'http://vladiuse.beget.tech/kupal/'
        response = requests.get(self.base + self.url, stream=True)
        # save file, see https://stackoverflow.com/a/13137873/7665691
        if response.status_code == 200:
            with open(path, 'wb') as file:
                for chunk in response:
                    file.write(chunk)
        static_path = path.replace('office/static/', '')
        return static_path


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