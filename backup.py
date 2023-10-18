import datetime
from urllib.parse import urlencode
import requests

def getting_a_token(app_id):
    # app_id = '51770037'
    oauth_base_url = 'https://oauth.vk.com/authorize'
    params = {
        'client_id': app_id,
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'display': 'page',
        'scope': 'status, photos',
        'response_type': 'token',
    }

    oauth_url = f'{oauth_base_url}?{urlencode(params)}'
    print(oauth_url)


class VKAPIClient:
    api_base_url = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v':'5.154'
        }

    def _build_url(self, api_metod):
        return f'{self.api_base_url}/{api_metod}'

    def _get_photos(self):
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': '-183', 'extended': '1'})
        response = requests.get(self._build_url('photos.get'), params=params)
        return response.json()

    def get_list_foto_max_quality(self):
        list_foto_all_info = self._get_photos()['response']['items']
        foto_list_for_download = []
        for id_, foto_info in enumerate(list_foto_all_info):
            list_foto = sorted(foto_info['sizes'], key=lambda x: x['width'], reverse=True)[0]
            list_foto.pop('type')
            list_foto['file_name'] = f'{id_}.jpg'
            foto_list_for_download.append(list_foto)
        return foto_list_for_download

    def creating_folder_in_yd(self, auth_token, path_folder):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Authorization': auth_token}
        params = {'path': path_folder}
        response = requests.put(url, headers=headers, params=params)
        print(f'Создана папка {path_folder} для backup фото из VK')

    def _copy_foto(self, path_folder, foto):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        path_file = f'{path_folder}{foto["file_name"]}'
        download_url = foto['url']
        headers = {'Authorization': auth_token}
        params = {'url': download_url,
                  'path': path_file}
        response = requests.post(url, headers=headers, params=params)
        upload_url = response.json()['href']
        response = requests.get(upload_url, headers=headers)
        return response.json()['status']

    def backup_photos_in_yd(self, auth_token):
        path_folder = f'disk:/backup foto from VK/{datetime.datetime.now()}/'
        self.creating_folder_in_yd(auth_token, path_folder)
        list_of_fotos = self.get_list_foto_max_quality()
        for foto in list_of_fotos:
            status = 'failed'
            i = 0
            while status == 'failed':
                status = self._copy_foto(path_folder, foto)
                i += 1
            if i == 1:
                print(f'Файл {foto["file_name"]} скопирован в {datetime.datetime.now()}!')
            else:
                print(f'Файл {foto["file_name"]} скопирован в {datetime.datetime.now()} с {i}-й потытки!')


if __name__ == '__main__':
    # app_id = input('Введите ID приложения: ')
    # getting_a_token(app_id)
    token = ('vk1.a.RHsSlNhRLUJe5Ay2LS4dMbaU_JLfCEWSDy6lqKJPNNOMe0OQ3sInskCu0t6WkHUpg3O4WgI47aaSLwOiZdclOTKHiB4HZ9rLz'
             'P18jdc72yigcWK_LgSnsgisp6w62jGoYpMKnHjbfUQ805OYy4tkrUbH9mauaiMqubM3ickQT4xBvgKOUqYjdMBh6yqz393ozmV_fgJB'
             'r4t-QpOza_5iug')
    user_id = input('Введите id пользователя VK: ')
    auth_token = input('Введите токен для доступа по API к яндекс-диску: ')
    vk_client = VKAPIClient(token, user_id)
    vk_client.backup_photos_in_yd(auth_token)
