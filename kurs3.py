import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlite3

# Замените 'token' на ваш ключ доступа к API
token = 'your_token'

# Создаем подключение к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Проверяем существование таблиц и создаем их, если не существуют
cursor.execute('''
    CREATE TABLE IF NOT EXISTS IDENTIFIER (
        user_id INTEGER PRIMARY KEY,
        answer VARCHAR(3)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS FAVORITES (
        user_id INTEGER PRIMARY KEY
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS BLACKLIST (
        user_id INTEGER PRIMARY KEY
    )
''')

# Сохраняем изменения в базе данных
conn.commit()


# Функция для отправки сообщения
def send_message(user_id, message, attachment=None):
    vk.messages.send(user_id=user_id, message=message, random_id=0, attachment=attachment)


# Функция для получения информации о пользователе
def get_user_info(user_id):
    fields = 'sex, bdate, city'  # Запрашиваем пол, дату рождения и город пользователя
    user_info = vk.users.get(user_ids=user_id, fields=fields)
    return user_info[0]


# Функция для получения списка пользователей противоположного пола
def get_opposite_sex_users(criteria):
    users = vk.users.search(count=1000, sex=criteria['opposite_sex'], city=criteria['city'], age_from=criteria['age'],
                            age_to=criteria['age'])
    return users['items']


# Функция для получения топ-3 популярных фотографий пользователя
def get_popular_photos(user_id):
    photos = vk.photos.get(owner_id=user_id, album_id='profile', extended=1, count=3)
    photos.sort(key=lambda x: x['likes']['count'], reverse=True)
    photo_urls = [photo['sizes'][-1]['url'] for photo in photos]
    return photo_urls


# Основной код бота
def main():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            user_info = get_user_info(user_id)

            criteria = {
                'city': user_info.get('city', ''),
                'age': 2024 - int(user_info.get('bdate', '').split('.')[-1]),
                'opposite_sex': 1 if user_info['sex'] == 2 else 2
            }

            opposite_sex_users = get_opposite_sex_users(criteria)

            if opposite_sex_users:
                selected_user = opposite_sex_users[0]  # Просто выбираем первого попавшегося пользователя

                user_name = selected_user['first_name'] + ' ' + selected_user['last_name']
                profile_link = 'https://vk.com/id' + str(selected_user['id'])
                photo_urls = get_popular_photos(selected_user['id'])

                send_message(user_id, f"Имя и фамилия: {user_name}\nСсылка на профиль: {profile_link}")

                for photo_url in photo_urls:
                    send_message(user_id, attachment=photo_url)

                # Запрос пользователю
                send_message(user_id, "Добавить пользователя в избранное? (ДА/НЕТ)")

                # Добавление информации о пользователе в таблицу "ИНДЕНТИФИКАТОР"
                cursor.execute("INSERT INTO IDENTIFIER (user_id, answer) VALUES (?, ?)", (user_id, ''))
                conn.commit()


# Вызов основной функции
if __name__ == "__main__":
    main()
