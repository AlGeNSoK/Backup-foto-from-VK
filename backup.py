import datetime
from urllib.parse import urlencode
import requests
import configuration

# Функция получение токена VK
def getting_a_token(app_id):
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
        params.update({'owner_id': self.user_id, 'album_id': 'profile', 'extended': '1'})
        response = requests.get(self._build_url('photos.get'), params=params)
        return response.json()

    def get_list_foto_max_quality(self):
        list_foto_all_info = self._get_photos()['response']['items']
        vk_photo_sizes = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
        foto_list_for_download = []
        file_name_list = []
        index = 2
        for foto_all_info in list_foto_all_info:
            file_name = foto_all_info["likes"]["count"]
            if file_name in file_name_list:
                file_name = f'{file_name}_{str(datetime.datetime.fromtimestamp(foto_all_info["date"]))}'
                if file_name in file_name_list:
                    file_name = f'{file_name}_{index}'
                    index += 1
            file_name_list.append(file_name)
            max_photo_size = max(foto_all_info['sizes'], key= lambda x: vk_photo_sizes[x['type']])
            max_photo_size['file_name'] = f'{file_name}.jpg'
            max_photo_size['size'] = max_photo_size.pop('type')
            foto_list_for_download.append(max_photo_size)
        return foto_list_for_download


class YDAPIclient:

    def __init__(self, auth_token):
        self.auth_token = auth_token

    def creating_folder_in_yd(self, path_folder):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Authorization': self.auth_token}
        params = {'path': path_folder}
        response = requests.put(url, headers=headers, params=params)
        print(f'Создана папка {path_folder} для backup фото из VK')

    def _copy_foto(self, path_folder, foto):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        path_file = f'{path_folder}{foto["file_name"]}'
        download_url = foto['url']
        headers = {'Authorization': self.auth_token}
        params = {'url': download_url,
                  'path': path_file}
        response = requests.post(url, headers=headers, params=params)
        upload_url = response.json()['href']
        response = requests.get(upload_url, headers=headers)
        return response.json()['status']

    def backup_photos_in_yd(self, list_of_fotos):
        path_folder = f'disk:/backup foto from VK/{datetime.datetime.now()}/'
        self.creating_folder_in_yd(path_folder)
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
    print('Запущенное приложение может сделать резервное копирование на яндекс-диск фотографий с Вашего профиля!')
    print('Для начала работы приложения необходимо открыть в браузере выданную ниже ссылку')
    getting_a_token(configuration.app_id)
    print('После входа в свой аккаунт VK необходимо из адресной строки браузера скопировать в приложение значение '
          'access_token')
    token = input('Введите значение access_token из адресной строки браузера: ')
    user_id = input('Введите id Вашего профиля в VK: ')
    vk_client = VKAPIClient(token, user_id)
    list_of_fotos = vk_client.get_list_foto_max_quality()
    auth_token_yd = input('Для доступа к яндекс-диску введите OAuth-токен диска: ')
    yd_client = YDAPIclient(auth_token_yd)
    yd_client.backup_photos_in_yd(list_of_fotos)