import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import shutil
import os
from datetime import datetime

# Замените 'group_token' на ваш токен группы
group_token = 'vk1.a.I9sjVOhePIoK9hZMNBB4pnvoOzohNd4JXmiTkBkSd8yjCVdfKG3lX6rJVxllIS-XUbwYCTRoCTjFUIKiPSex48CiKHb1i3x9r34KbUcLp4zK_DLDOftxMpUTeuxM1t82cbHZY1T6q5Dxbm8gcHxVkGm79R6Q0bXLxd54YNNQ9qYoGyFPgeGpG8hLHfv_9sXHg3lmUjLtV0l88m8n71qq1w'

# Создание экземпляра VkApi с токеном группы
vk_session = vk_api.VkApi(token=group_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Путь для сохранения фотографии профиля
save_path = "F:\\Programs\\Python_Git\\kurs3_arch\\profile_photo.jpg"

def download_photo_and_save(user_id, save_path):
    # Получение информации о пользователе
    user_info = vk.users.get(user_ids=user_id, fields='photo_max_orig,bdate,city,sex')

    # Получение ссылки на фото профиля пользователя
    photo_url = user_info[0]['photo_max_orig']

    # Скачивание фото и сохранение в указанную папку
    response = requests.get(photo_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
        return user_info[0]
    else:
        return None

def send_photo_and_info(user_id, photo_path, user_info):
    upload_url = vk.photos.getMessagesUploadServer()['upload_url']
    files = {'photo': open(photo_path, 'rb')}
    response = requests.post(upload_url, files=files)
    photo_data = response.json()
    photo = vk.photos.saveMessagesPhoto(**photo_data)
    attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
    message = f"Ваш год рождения: {user_info['bdate']}\n" if 'bdate' in user_info else "Информация о годе рождения недоступна\n"
    message += f"Ваш город: {user_info['city']['title']}\n" if 'city' in user_info else "Информация о городе недоступна\n"
    message += f"Ваш пол: {'мужской' if user_info['sex'] == 2 else 'женский'}\n" if 'sex' in user_info else "Информация о поле недоступна\n"
    vk.messages.send(user_id=user_id, message=message, attachment=attachment, random_id=0)

# Пример использования
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if event.text.lower() == "привет":
            # Используем ID пользователя, отправившего сообщение "привет"
            user_id = event.user_id
            # Скачиваем фотографию профиля пользователя и получаем информацию о пользователе
            user_info = download_photo_and_save(user_id, save_path)
            if user_info:
                print("Фотография профиля успешно сохранена.")
                # Отправляем фотографию и информацию пользователю
                send_photo_and_info(user_id, save_path, user_info)
            else:
                print("Ошибка при скачивании фотографии профиля.")

