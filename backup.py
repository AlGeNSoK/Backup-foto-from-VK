import datetime
from urllib.parse import urlencode
from vk_api import VKAPIClient
from yd_api import YDAPIclient


# Функция получение токена VK
def getting_a_token(app_id):
    """
    Функция получения токена VK
    :param app_id:
    :return:
    """
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

def entering_number_of_photos():
    """
    Функция ввода количества фотографий
    :return:
    """
    while True:
        try:
            number_of_photos = int(input('Укажите количество фотографий, которое необходимо сохранить на яндекс-диске'
                                         ' (чтобы отказаться от резервного копирования введите 0): '))
        except ValueError:
            print('Вы ввели неверное значение!\n'
                  'Введите цифру больше нуля.')
        else:
            if number_of_photos < 0:
                print('Вы ввели отрицательное или нулевое значение!\n'
                      'Введите цифру больше нуля.')
            elif number_of_photos == 0:
                break
            else:
                if number_of_photos > len(list_of_photos):
                    print('Вы ввели цифру, превышающую количество фотографий в профиле VK, '
                          'поэтому будут сохранены все фотографии!')
                    number_of_photos = len(list_of_photos)
                creating_folder_and_copy_photos(number_of_photos)
                break

def output_list_of_photos(list_of_photos):
    """
    Функция вывода списка фотографий профиля VK
    :param list_of_photos:
    :return:
    """
    print(f'В Вашем профиле VK {len(list_of_photos)} фотографий:')
    for index, photo in enumerate(list_of_photos):
        print(f'{index + 1}. {photo["url"]}')

def creating_folder_and_copy_photos(number_of_photos):
    """
    Функция создания папки на яндекс-диске и копирования фото
    :param number_of_photos:
    :return:
    """
    yd_client = YDAPIclient(auth_token_yd)
    while True:
        folder_name = input('Задайте имя папки, в которую необходимо сохранить '
                            'фотографии: ')
        path_folder = f'disk:/{folder_name}/'
        response = yd_client.creating_folder_in_yd(path_folder)
        status_operation = response.status_code
        if status_operation == 201:
            print(f'Создана папка {folder_name} для backup фото из VK в '
                  f'{datetime.datetime.now()}!')
            yd_client.backup_photos_in_yd(list_of_photos[:number_of_photos], path_folder)
            break
        elif status_operation == 401:
            print('Отсутствует доступ к яндекс-диску!\n'
                  'Введите правильный OAuth-токен яндекс-диска в настройках '
                  'приложения.')
            break
        elif status_operation == 409:
            print('Задано неправильное название папки!')
        else:
            print(f'Ошибка: {response.json().get("message")}\n'
                  f'Проверьте все настройки приложения и попробуйте заново сделать'
                  f' резервное копирование фотографий.')
            break


if __name__ == '__main__':
    app_id = '51770037'
    token= ''
    user_id = ''
    auth_token_yd = ''
    print('Запущенное приложение может сделать резервное копирование на яндекс-диск фотографий с Вашего профиля!')
    while True:
        print('\n'
              '1. Предварительная настройка приложения.\n'
              '2. Резервное копирование фотографий.\n'
              '3. Выход из приложения.\n')
        try:
            action = int(input('Введите необходимый пункт меню (1-3): '))
        except:
            pass
        else:
            if action == 1:
                while True:
                    print('\n'
                          '1. Получение и ввод access_token для доступа к VK.\n'
                          '2. Ввод id профиля VK.\n'
                          '3. Ввод OAuth-токена яндекс-диска.\n'
                          '4. Выход в главное меню.\n')
                    try:
                        settings_action = int(input('Введите необходимый пункт меню (1-4): '))
                    except:
                        pass
                    else:
                        if settings_action == 1:
                            getting_a_token(app_id)
                            print('1. Откройте в браузере выданную выше ссылку.\n'
                                  '2. После входа в свой аккаунт VK необходимо из адресной строки браузера скопировать '
                                  'значение access_token.\n')
                            token = input('Введите значение access_token из адресной строки браузера: ')
                        elif settings_action == 2:
                            user_id = input('Введите id Вашего профиля в VK: ')
                        elif settings_action == 3:
                            auth_token_yd = input('Для доступа к яндекс-диску введите OAuth-токен диска: ')
                        elif settings_action == 4:
                            break
            elif action == 2:
                if token and user_id and auth_token_yd:
                    vk_client = VKAPIClient(token, user_id)
                    list_of_photos, status = vk_client.get_list_foto_max_quality()
                    if status == 'success':
                        if len(list_of_photos) > 0:
                            output_list_of_photos(list_of_photos)
                            entering_number_of_photos()
                        else:
                            print('\n'
                                  'В указанном профиле VK отсутствуют фотографии')
                else:
                    print('Не все параметры доступа к VK и яндекс диску заданы!\n'
                          'Сначала выполните первоначальную настройку приложения.')
            elif action == 3:
                break
