import time
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from application.db.work_with_database import Users, Customers, Candidates
from var_name import token_app, token_group
import requests


class VK:
    url = 'https://api.vk.com/method/'
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.couple_id = 0
        self.user = db.MainUser
        self.offset = 0
        self.couple_id = 0
        self.couple_name = ''
        self.top_photo = ''

    def name(self):
        name = self.info()[0]['first_name']
        return name

    def info(self):
        info = bot_vk.method("users.get", {"user_ids": self.user_id,
                                           "fields": 'sex, bdate, city, relation'})
        return info

    def get_age(self, user_id):
        if 'bdate' in self.info()[0].keys():
            bdate = self.info()[0]['bdate']
            if bdate is not None and len(bdate.split('.')) == 3:
                birth = datetime.strptime(bdate, '%d.%m.%Y').year
                this = datetime.now().year
                age = this - birth
                return age
            else:
                return 'Возраст неизвестен'
        else:
            return 'Возраст неизвестен'

    def get_sex(self, user_id):
        sex = self.info()[0]['sex']
        if sex == 1:
            return 2
        elif sex == 2:
            return 1
        else:
            return 0

    def get_city(self, user_id):
        if 'city' in self.info()[0].keys():
            city = self.info()[0]['city']['id']
            return city
        else:
            return 0

    def relation(self):
        if 'relation' in self.info()[0].keys():
            relation = self.info()[0]['relation']
            return relation
        else:
            return 'Скрыто семейное положение'

    def bot_start(self):
        db.create_tables()
        self.name()
        self.age()
        self.city()
        self.relation()
        try:
            self.user = db.MainUser(vk_id=self.user_id, name=self.name(), age=self.age(),
                                    city=self.city(), relation=self.relation())
            db.add_user(self.user)
        except IntegrityError:
            pass
        self.find_couple()
        self.get_top_photo()
        write_msg(event.user_id, f'Посмотри кого нашли:\n'
                                 f'Имя: {self.couple_name}, ссылка: vk.com/id{self.couple_id}', self.top_photo)
        return self.couple()

    def couple(self):
        write_msg(event.user_id, f'Пиши ДАЛЕЕ, чтобы продолжить поиск, и сохранить человека в базе данных, '
                                 f'или пиши СТОП, чтобы не искать, или ПРОПУСТИТЬ, чтобы пропустить человека '
                                 f'и искать следующего, если пропустишь, пара снова найдется.')
        while True:
            for new_event in longpoll.listen():
                if new_event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if new_event.message.lower() == 'далее':
                        try:
                            found_couple = db.CoupleUser(vk_id=self.couple_id, name=self.couple_name,
                                                         id_main_user=self.user_id)
                            db.add_user(found_couple)
                        except IntegrityError:
                            pass
                        write_msg(event.user_id, 'Ищу следующую пару...')
                        self.offset += 1
                        self.find_couple()
                        self.get_top_photo()
                        write_msg(event.user_id, f'Посмотри кого нашли:\n'
                                                 f'Имя: {self.couple_name}, ссылка: vk.com/id{self.couple_id}',
                                                 self.top_photo)
                        return self.couple()
                    elif new_event.message.lower() == 'стоп' or new_event.message.lower() == 'нет':
                        write_msg(event.user_id, 'Заканчиваем поиск, если хочешь продолжить, пиши ПРОДОЛЖИТЬ.')
                    elif new_event.message.lower() == 'продолжить' or new_event.message.lower() == 'пропустить':
                        write_msg(event.user_id, f'Ищу следующую пару...')
                        self.offset += 1
                        self.find_couple()
                        self.get_top_photo()
                        write_msg(event.user_id, f'Посмотри кого нашли:\n'
                                                 f'Имя: {self.couple_name}, ссылка: vk.com/id{self.couple_id}',
                                  self.top_photo)
                        return self.couple()

    def find_couple(self):
        resp = user_vk.method('users.search', {'count': 1, 'city': self.city(), 'sex': self.sex(), 'age': self.age(),
                                               'relation': self.relation(), 'offset': self.offset, 'status': (1, 6),
                                               'has photo': 1, 'fields': 'is_closed'})
        if resp['items'][0]['id'] in db.check_user():
            self.offset += 1
            self.find_couple()
        else:
            if resp['items']:
                for couple in resp['items']:
                    if couple['is_closed']:
                        self.offset += 1
                        self.find_couple()
                    else:
                        self.couple_id = couple['id']
                        self.couple_name = couple['first_name']
            else:
                self.offset += 1
                self.find_couple()

    def get_top_photo(self):
        photo_list = []
        resp = user_vk.method('photos.get', {'owner_id': self.couple_id,
                                             'album_id': 'profile',
                                             'access_token': my_token,
                                             'extended': 1,
                                             'v': '5.131'})
        photos = []
        for photo in resp['items']:
            photo_info = {'id': photo['id'], 'owner_id': photo['owner_id'], }
            count = 0
            try:
                count_com = user_vk.method('photos.getComments', {'owner_id': self.couple_id, 'photo_id': photo['id']})
                count = count_com['count']
            except ApiError:
                pass
            photo_info['popular'] = photo['likes']['count'] + count
            photo_list.append(photo_info)
        photo_list = sorted(photo_list, key=lambda k: k['popular'], reverse=True)
        for i in photo_list:
            photos.append(f"photo{i['owner_id']}_{i['id']}")
        self.top_photo = ','.join(photos[:3])
        return self.top_photo 
    
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def getvk(self, url, new_params, *kwargs):
        params = self.params.copy()
        params.update(new_params)
        response = requests.get(url, params=params, *kwargs)
        response.raise_for_status()
        result = response.json()
        if 'error' in result:
            print(f'Код ошибки: {result["error"]["error_code"]}')
            if result["error"]["error_code"] == 5:
                print('ключ не валидный')
            elif result["error"]["error_code"] == 27:
                print('введен ключ группы')
            return None
        return result['response']

    def get_cities(self, city, region):
        city_search_url = self.url + 'database.getCities'
        city_search_params = {
            'q': city,
            'country_id': 1,
            'count': 100
        }
        result = self.getvk(url=city_search_url, new_params=city_search_params)
        item_temp = 0
        for item in result['items']:
            if item.get('region') is None:
                item_temp = item['id']
                break
            _region = item['region'].split(' ')[0].lower()
            if item['title'].lower() == city.lower() and _region == region.lower():
                item_temp = item['id']
                break
        if result is None:
            return None
        return item_temp

    def user_get(self, search_string):
        users_search_url = self.url + 'users.search'
        users_search_params = {
            'q': search_string,
            'count': 1
        }
        result = self.getvk(url=users_search_url, new_params=users_search_params)
        if result is None:
            return None
        return result['items']

    def get_people_list(self, find_param):
        users_search_url = self.url + 'users.search'
        users_search_params = {
            'age_from': find_param['возраст от'],
            'age_to': find_param['возраст до'],
            'sex': find_param['пол'],
            'city': find_param['город'],
            'relation': find_param['семейное положение'],
            'fields': 'bdate, is_no_index, is_closed, can_access_closed, '
                      'city, home_town, sex, status, photo, relation'
        }
        result = self.getvk(url=users_search_url, new_params=users_search_params)
        return result['items']

    def get_user_get(self, user_ids):
        users_get_url = self.url + 'users.get'
        users_get_params = {
            'user_ids': user_ids,
            'fields': 'bdate, is_closed, domain, friend_status, has_photo, '
                      'is_friend, screen_name, site, photo, relation'
        }
        result = self.getvk(url=users_get_url, new_params=users_get_params)
        return result['items']

    def photos_get(self, album, ext=0, owner_id=None):
        """
        Параметры album_id (идентификатор альбома)
        wall — фотографии со стены;
        profile — фотографии профиля;
        saved — сохраненные фотографии. Возвращается только с ключом доступа пользователя.
        Параметры extended
        0 - по умолчанию - дополнительные поля не возвращаются
        1 — будут возвращены дополнительные поля likes, comments, tags, can_comment, reposts.
        """
        photos_get_url = self.url + 'photos.get'
        photos_get_params = {
            'album_id': album,
            'extended': ext,
            'owner_id': owner_id
        }
        result = self.getvk(url=photos_get_url, new_params=photos_get_params)
        return result['items']

    def get_contact_information(self, user_id):
        users_get_url = self.url + 'users.get'
        users_get_params = {
            'user_ids': user_id,
            'fields': 'is_closed, can_access_closed, bdate, city, country, '
                      'first_name_, home_town, last_name_, relation, sex, status, photo'
        }
        return self.getvk(url=users_get_url, new_params=users_get_params)

    def find_user(self, user_id):
        #по полученным данным найдем человека (автопоиск)
        url = f'https://api.vk.com/method/users.search'
        params = {'access_token': user_token_vk,
                  'v': '5.131',
                  'sex': self.get_sex(user_id),
                  'age': self.get_age(user_id),
                  'city': self.city(user_id),
                  'fields': 'is_closed',
                  'fields': 'id',
                  'fields': 'first_name',
                  'fields': 'last_name',
                  'status': '1' or '6',
                  'count': 500}
        resp = requests.get(url, params=params)
        resp_json = resp.json()
        try:
            dict_1 = resp_json['response']
            list_1 = dict_1['items']
            for person_dict in list_1:
                if person_dict.get('is_closed') == False:
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'vk.com/id' + str(person_dict.get('id'))
                    insert_data_users(first_name, last_name, vk_id, vk_link)
                else:
                    continue
            return f'Поиск завершён'
        except KeyError:
            self.write_msg(user_id, 'Ошибка при получении токена')

class ChatBot:
    # нельзя использовать токен пользователя, только токен группы
    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)

    def connect_longpoll(self):
        return VkLongPoll(self.vk)

    def write_msg(self, user_id, message, attachment):
        print(f'ChatBot ответил пользователю {user_id} сообщением:\n{message}:')
        self.vk.method('messages.send', {
            'user_id': user_id,
            'message': message,
            'attachment': attachment,
            'random_id': randrange(10 ** 7),
        })

    def get_user_get(self, user_id):
        req = self.vk.method('users.get', {
            'user_ids': user_id,
            'fields': 'is_closed, can_access_closed, bdate, city, country, first_name_, '
                      'home_town, last_name_, relation, sex, status, photo, schools'
        })
        return req

session = Session()
# для подключения к VkApi используем только токен группы
chat_bot = ChatBot(token_group)
longpoll = chat_bot.connect_longpoll()

user_data_master = {
    'is_closed': False,
    'can_access_closed': False,
    'bdate': '',
    'city': {'id': -1, 'title': ''},
    'country': -1,
    'first_name': '',
    'home_town': '',
    'last_name': '',
    'relation': 0,
    'sex': 0,
    'status': '',
    'photo': '',
    'schools': []
}

sex_list = {0: 'не указано', 1: 'женский', 2: 'мужской'}
relation_list = {
    0: 'не указано',
    1: 'не женат/не замужем',
    2: 'есть друг/есть подруга',
    3: 'помолвлен/помолвлена',
    4: 'женат/замужем',
    5: 'всё сложно',
    6: 'в активном поиске',
    7: 'влюблён/влюблена',
    8: 'в гражданском браке',
}

user_token_tuple = {}

def create_message_help_new():
    return "Будет неплохо, если вы предоставите свой токен пользователя:\n" \
           "Для этого введите команду: /токен ваш_токен\n" \
           "Затем, можно вводить критерии поиска, с помощью команды:\n" \
           "/найди возраст_от возраст_до пол город регион семейное_положение\n" \
           "   например: /найди 25 30 1 Москва Московская 6\n" \
           "   --------------------------\n" \
           "   варианты пол\n" \
           "   1 - женский;\n" \
           "   2 - мужской;\n" \
           "   варианты С_П\n" \
           "   1 - не женат/не замужем;\n" \
           "   2 - есть друг/есть подруга;\n" \
           "   3 - помолвлен/помолвлена;\n" \
           "   4 - женат/замужем;\n" \
           "   5 - всё сложно;\n" \
           "   6 - в активном поиске;\n" \
           "   7 - влюблён/влюблена;\n" \
           "   8 - в гражданском браке;\n"

def added_customer_orm(id_user, user_id):
    # добавление пользователя VK в базу customers
    user_in_customer = session.query(Customers).join(
        Users, Users.id_user == Customers.id_user).filter(
        Users.user_id == user_id).first()
    if user_in_customer is None:
        print(f'+пользователя {user_id} нет в базе customers')
        user_in_customer = Customers(id_user=id_user)
        session.add(user_in_customer)
        session.commit()
        print(f'+пользователь {user_id} добавлен в базу customers')
    return user_in_customer.id_customer

def find_candidate_orm(id_user, user_id):
    # ищет человека в таблице candidates с привязкой к пользователю
    user_in_candidate = session.query(Users).join(
            Candidates, Users.id_user == Candidates.id_user).filter(
            Users.user_id == user_id).first()
    if user_in_candidate is None:
        print(f'+пользователя {user_id} нет в базе кандидатов')
        new_customer = Customers(id_user=id_user)
        session.add(new_customer)
        session.commit()
        print(f'+пользователь {user_id} добавлен в базу кандидатов')

def added_user_orm(user_id, user_data):
    user = session.query(Users).filter(Users.user_id == user_id).first()
    if user is None:
        print(f'+пользователь {user_id} НЕ найден в базе пользователей')
        user = Users(user_id=user_data['id'],
                     first_name=user_data['first_name'],
                     last_name=user_data['last_name'],
                     id_city=user_data['city']['id'],
                     bdate=user_data['bdate'],
                     is_closed=user_data['is_closed'],
                     id_relation=EnumRelations(user_data['relation']).name,
                     id_sex=EnumSex(user_data['sex']).name,
                     )
        session.add(user)
        session.commit()
    else:
        print(f'+пользователь {user_id} найден в базе пользователей')
    return user.id_user

def get_search_parameters(argument, token):
    key = ['возраст от', 'возраст до', 'пол', 'город', 'регион', 'семейное положение']
    find_param = {k: v for k, v in zip(key, argument)}
    find_msg = 'Вы ввели следующие критерии поиска. Начинаю поиск\n'
    for k, v in find_param.items():
        if k == 'пол':
            msg = sex_list[int(v)]
            find_msg = find_msg + f'{k}: {msg}\n'
        elif k == 'семейное положение':
            msg = relation_list[int(v)]
            find_msg = find_msg + f'{k}: {msg}\n'
        else:
            find_msg += f'{k}: {v}\n'
    find_param['возраст от'] = int(find_param['возраст от'])
    find_param['возраст до'] = int(find_param['возраст до'])
    find_param['пол'] = int(find_param['пол'])
    vk_client = VK(token, '5.131')
    id_city = vk_client.get_cities(find_param['город'], find_param['регион'])
    if id_city is None:
        find_msg = ''
    find_param['город'] = id_city
    find_param['семейное положение'] = int(find_param['семейное положение'])
    return find_msg, find_param

def candidate_list_processing(user_id, user_chat, find_param, token):
    # функция обработки списка кандидатов
    vk_client = VK(token, '5.131')
    people_data = vk_client.get_people_list(find_param)
    id_user = added_user_orm(user_id, user_chat)
    id_customer = added_customer_orm(id_user, user_id)
    msg_attachment = ''
    for item in people_data:
        if item['is_closed']:
            continue
        user_people = user_data_master.copy()
        user_people.update(item)
        candidate_user_id = item['id']
        candidate_id_user = added_user_orm(candidate_user_id, user_people)
        response = session.query(Customers).filter_by(id_customer=id_customer).first().candidates
        no_find_flag = True
        for item_candidate in response:
            if item_candidate.id_user == candidate_id_user:
                no_find_flag = False
                break
        if no_find_flag:
            adding_customers_and_candidates(id_customer, candidate_id_user)
            candidate_user_url = 'https://vk.com/id' + str(candidate_user_id)
            result_token = user_dictionary_processing_online(user_id)
            if not result_token:
                result_token = token_app
            tuple_photos = photo_list_processing(candidate_user_id, result_token)
            for item_attach in tuple_photos:
                msg_attachment += f"photo{item_attach[3]}_{item_attach[2]},"
            msg_attachment = msg_attachment.rstrip(',')
            return candidate_user_url, msg_attachment
    return None, None

def adding_customers_and_candidates(id_customer, candidate_id_user):
    # добавление заказчиков и кандидатов
    customer = session.query(Customers).filter(Customers.id_customer == id_customer).first()
    candidate = session.query(Candidates).filter(Candidates.id_user == candidate_id_user).first()
    if candidate is None:
        candidate = Candidates(id_user=candidate_id_user)
        session.add(candidate)
        session.flush()
    customer.candidates.append(candidate)
    session.add(customer)
    session.commit()

def photo_list_processing(candidate_user_id, token):
    # обработка списка фотографий
    vk_client = VK(token, '5.131')
    list_photos_vk = vk_client.photos_get('profile', 1, candidate_user_id)
    list_photos = []
    for item_photo in list_photos_vk:
        for item_sizes in item_photo['sizes']:
            if item_sizes['type'] == 'm' and item_sizes['url'][-4:] == '.jpg':
                new_tuple = (item_photo['likes']['count'],
                             item_sizes['url'],
                             item_photo['id'],
                             item_photo['owner_id'])
                list_photos.append(new_tuple)
    temp_photos = tuple(list_photos)
    temp_photos = tuple(sorted(temp_photos))
    tuple_photos = temp_photos[:-4:-1]
    return tuple_photos

def find_command_processing(user_id, user_chat, argument):
    # обработка команды найди
    if argument[0] == '?':
        print('# выводим список команд получения данных о пользователе')
        message = create_message_help_new()
        chat_bot.write_msg(user_id, message, 'attachment')
    else:
        if len(argument) == 6:
            if argument[0].isdigit() and argument[1].isdigit() and \
                    argument[2].isdigit() and argument[5].isdigit():
                result_token = user_dictionary_processing_online(user_id)
                if not result_token:
                    result_token = token_app
                find_msg, find_param = get_search_parameters(argument, result_token)
                if find_param is not None:
                    chat_bot.write_msg(user_id, find_msg, 'attachment')
                    result_token = user_dictionary_processing_online(user_id)
                    if not result_token:
                        result_token = token_app
                    message, msg_attach = candidate_list_processing(user_id, user_chat, find_param, result_token)
                    if message is not None:
                        chat_bot.write_msg(user_id, message, msg_attach)
                    else:
                        message = 'Все кандидаты подходящие к вашим критериям поиска,\n' \
                                  'вам уже предоставлены\n' \
                                  'Для продолжения поиска, введите другие критерии поиска'
                        chat_bot.write_msg(user_id, message, 'attachment')
                else:
                    message = 'Введены некорректные параметры, повторите ввод'
                    chat_bot.write_msg(user_id, message, 'attachment')
            else:
                message = 'Последовательность параметров нарушена, повторите ввод'
                chat_bot.write_msg(user_id, message, 'attachment')
        else:
            message = 'Вы ввели не все параметры, повторите ввод'
            chat_bot.write_msg(user_id, message, 'attachment')

def user_dictionary_processing_online(user_id, user_token=''):
    # обработка словаря пользователей он-лайн
    current_time = int(time.time())
    if user_id in user_token_tuple:
        tmp_user_token, tmp_time_user = user_token_tuple[user_id]
        if not user_token:
            user_token = tmp_user_token
    user_token_tuple[user_id] = [user_token, current_time]
    return user_token

def deleting_offline_users_from_dictionary():
    # удаление пользователей офф лайн из словаря
    current_time = int(time.time())
    for key, value in user_token_tuple.items():
        if value[1] - current_time > 3600:
            del user_token_tuple[key]

def getting_token(user_id, argument):
    if len(argument) > 0:
        token_user = argument[0]
        vk_client = VK(token_user, '5.131')
        result = vk_client.user_get('Vasya Babich')
        if result is not None:
            user_dictionary_processing_online(user_id, token_user)
            message = f'вы сообщили следующий токен: {token_user}'
            chat_bot.write_msg(user_id, message, 'attachment')
        else:
            message = 'Вы ввели некорректный токен. Повторите ввод\n' \
                      'Для этого введите команду: /токен ваш_токен\n' \
                      'Или наберите опять команду /знакомство'
            chat_bot.write_msg(user_id, message, 'attachment')
    else:
        message = 'Вы не ввели токен. Повторите ввод\n' \
                  'Для этого введите команду: /токен ваш_токен'
        chat_bot.write_msg(user_id, message, 'attachment')

def command_processing(user_id, user_chat, request):
    input_msg = request[1:].split(' ')
    print('вошли в обработку команд')
    command = input_msg[0]
    argument = input_msg[1:]
    if command == 'знакомство':
        id_user = added_user_orm(user_id, user_chat)
        added_customer_orm(id_user, user_id)
        message = create_message_help_new()
        chat_bot.write_msg(user_id, message, 'attachment')
    elif command == 'найди':
        print('# обработка команд критериев поиска')
        find_command_processing(user_id, user_chat, argument)
    elif command == 'токен':
        getting_token(user_id, argument)

def main():
    # поговорить с чат-ботом
    Base.metadata.create_all(engine)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()
            user_id = event.user_id
            user_dictionary_processing_online(user_id)
            deleting_offline_users_from_dictionary()
            user = chat_bot.get_user_get(user_id)[0]
            user_chat = user_data_master.copy()
            user_chat.update(user)
            if request.startswith('/'):
                command_processing(user_id, user_chat, request)
            elif request == "привет":
                message = f"Привет, {user_chat['first_name']}\n" \
                          f"Я ЧатБот для знакомств. Могу найти Вам пару\n" \
                          f"Если хотите, напишите мне '/знакомство'"
                chat_bot.write_msg(user_id, message, 'attachment')
            elif request == "пока":
                chat_bot.write_msg(user_id, "Пока((", 'attachment')
            else:
                chat_bot.write_msg(user_id, "Не понял вашего ответа...", 'attachment')

if __name__ == '__main__':
    main()
