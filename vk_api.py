import requests
import datetime


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
        return response

    def get_list_foto_max_quality(self):
        reply = self._get_photos()
        foto_list_for_download = []
        try:
            list_foto_all_info = reply.json()['response']['items']
        except:
            status = 'error'
            print(f'\n'
                  f'Ошибка: {reply.json()["error"]["error_msg"]}')
        else:
            status = 'success'
            vk_photo_sizes = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
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
        return foto_list_for_download, status
