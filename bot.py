import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import sqlite3

GENRES = ['драма', 'детектив', 'криминал', 'триллер', 'комедия', 'романтика']  # жанры для быстрого поиска


class Bot:

    def __init__(self):
        self.con = sqlite3.connect("TheBot.db")  # подключаем бд
        self.cur = self.con.cursor()

        self.vk_session = vk_api.VkApi(  # передаем ключ доступа к управлению группой
            token='64c760ee5cf77502cf3eb06d7c1e885191933969908fd8027ffbfdb5a3ab6005d27fdbfde231f517f72ab')
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, 194931281)  # передаем id группы

        self.keyboard = VkKeyboard(one_time=False)  # создаем дефолтную клавиатуру(кнопочки) для взаимодействия с юзером
        self.keyboard.add_button(label="Вспомнить сериал", color=VkKeyboardColor.POSITIVE)
        self.keyboard.add_line()
        self.keyboard.add_button(label="Посоветуйте что-нибудь", color=VkKeyboardColor.PRIMARY)

        self.advise_keyboard = VkKeyboard(
            one_time=False)  # клавиатура для параметров поиска сериала для функции 'посоветовать'
        self.advise_keyboard.add_button(label="Аниме", color=VkKeyboardColor.POSITIVE)
        self.advise_keyboard.add_button(label="Сериал", color=VkKeyboardColor.POSITIVE)
        self.advise_keyboard.add_line()
        self.advise_keyboard.add_button(label="Драма", color=VkKeyboardColor.PRIMARY)
        self.advise_keyboard.add_button(label="Детектив", color=VkKeyboardColor.PRIMARY)
        self.advise_keyboard.add_button(label="Комедия", color=VkKeyboardColor.PRIMARY)
        self.advise_keyboard.add_line()
        self.advise_keyboard.add_button(label="Триллер", color=VkKeyboardColor.PRIMARY)
        self.advise_keyboard.add_button(label="Криминал", color=VkKeyboardColor.PRIMARY)
        self.advise_keyboard.add_button(label="Романтика", color=VkKeyboardColor.PRIMARY)
        self.advise_keyboard.add_line()
        self.advise_keyboard.add_button(label="Что угодно, смотреть нечего(", color=VkKeyboardColor.DEFAULT)

        self.search_keyboard = VkKeyboard(one_time=False)
        self.search_keyboard.add_button(label="Да", color=VkKeyboardColor.POSITIVE)
        self.search_keyboard.add_button(label="Нет", color=VkKeyboardColor.NEGATIVE)
        self.search_keyboard.add_line()
        self.search_keyboard.add_button(label="Вспомнилось!", color=VkKeyboardColor.PRIMARY)
        self.search_keyboard.add_button(label="Отмена", color=VkKeyboardColor.DEFAULT)

    def main(self):  # основная функция
        for event in self.longpoll.listen():  # цикл - слушаем, что будет происходить в группе
            if event.type == VkBotEventType.MESSAGE_NEW:  # если нам написали, проходимся по условным операторам
                if event.obj.message['text'].lower() == 'привет':
                    self.vk.messages.send(user_id=event.obj.message['from_id'],
                                          message="Ну приветушки-омлетушки, я - бот, который в будущем будет помогать тебе "
                                                  "вспомнить, на какой серии любимого сериала ты остановился! или "
                                                  "остановилась... А пока воть, смотри какое тут солнышко: vk.com/id" + str(
                                              event.obj.message['from_id']) + "\nА теперь напиши начать",
                                          random_id=random.randint(0, 2 ** 64))
                elif event.obj.message['text'].lower() == 'начать':
                    self.vk.messages.send(peer_id=event.obj.message['from_id'],
                                          message="Приветик, " + str(
                                              self.vk.users.get(user_id=event.obj.message['from_id'])[0][
                                                  'first_name']) + "! Выбери кнопку!",
                                          random_id=random.randint(0, 2 ** 64),
                                          keyboard=self.keyboard.get_keyboard())
                elif event.obj.message['text'].lower() == 'вспомнить сериал':
                    self.vk.messages.send(user_id=event.obj.message['from_id'],
                                          message="Для начала выбери сериал, который тебя интересует(напиши его название)",
                                          random_id=random.randint(0, 2 ** 64))
                elif event.obj.message['text'].lower() == 'посоветуйте что-нибудь':
                    self.vk.messages.send(user_id=event.obj.message['from_id'],
                                          message="что предпочитаете?",
                                          random_id=random.randint(0, 2 ** 64),
                                          keyboard=self.advise_keyboard.get_keyboard())  # передаем клавиатуру для советов
                elif event.obj.message['text'].lower() == 'аниме':
                    result = self.cur.execute("""SELECT name FROM seriales WHERE тип=1""").fetchall()
                    self.vk.messages.send(peer_id=event.obj.message['from_id'],
                                          message=str(random.choice(result)[0]),
                                          random_id=random.randint(0, 2 ** 64),
                                          keyboard=self.keyboard.get_keyboard())  # когда нажали кнопку, возвращаемся к
                    # предыдущей клавиатуре
                elif event.obj.message['text'].lower() == 'сериал':
                    result = self.cur.execute("""SELECT name FROM seriales WHERE тип=2""").fetchall()
                    self.vk.messages.send(peer_id=event.obj.message['from_id'],
                                          message=str(random.choice(result)[0]),
                                          random_id=random.randint(0, 2 ** 64),
                                          keyboard=self.keyboard.get_keyboard())
                elif event.obj.message['text'].lower() in GENRES:  # если запрос есть в жанрах, мы берем жанр из таблицы
                    # и вычисляем из него случайный
                    genres, result = self.cur.execute("""SELECT name, жанр FROM seriales""").fetchall(), []
                    for elem in genres:  # алгоритм вычисления
                        if event.obj.message['text'].lower() in elem[1].split(','):
                            result.append(elem[0])
                    self.vk.messages.send(peer_id=event.obj.message['from_id'],
                                          message=str(random.choice(result)),
                                          random_id=random.randint(0, 2 ** 64),
                                          keyboard=self.keyboard.get_keyboard())
                elif event.obj.message['text'].lower() == 'что угодно, смотреть нечего(':
                    serial, typ = random.choice(self.cur.execute("""SELECT name, тип FROM seriales""").fetchall())
                    serial_type = self.cur.execute(f"""SELECT typ FROM type WHERE id={typ}""").fetchall()[0][0]
                    self.vk.messages.send(peer_id=event.obj.message['from_id'],
                                          message=str(serial_type) + " " + str(serial),
                                          random_id=random.randint(0, 2 ** 64),
                                          keyboard=self.keyboard.get_keyboard())
                elif event.obj.message['text'].lower() in self.sql_fetch():  # проверка, находится ли спрашиваемый
                    # сериал в таблицах
                    self.vk.messages.send(user_id=event.obj.message['from_id'],
                                          message="тааакс, нашла в своих записях нужный файлик. теперь я буду задавать "
                                                  "тебе вопросы-вспоминалки, а ты отвечай \'да\' или \'нет\', ну или "
                                                  "же \'вспомнилось!\'(если оно и правда вспомнилось), а также если "
                                                  "захочешь отменить свой запрос",
                                          random_id=random.randint(0, 2 ** 64))
                    self.searching(event.obj.message['text'].lower(),
                                   event.obj.message['from_id'])  # запускается функция,
                    # в которую передаем название сериала и id юзера
                else:  # если ничего не подошло, говорим, что такого сериала нет
                    self.vk.messages.send(user_id=event.obj.message['from_id'],
                                          message="оу, такого сериала я пока не знаю...",
                                          random_id=random.randint(0, 2 ** 64))

    def searching(self, name,
                  user):  # функция,осуществляющая поиск серии. параметр name - имя сериала, user - id пользователя
        series = self.cur.execute(f"SELECT Сезон FROM '{name}' ").fetchall()  # находим кол-во серий в каждом сезоне
        # нужного нам сериала
        max_series = 0  # эти два параметра - нижняя и верхняя границы
        min_seires = 0
        seasons = []
        users_season = 0
        for elem in series:
            seasons.append(elem[0])  # записываем кол-во серий в каждом сезоне в список в более удобном формате
            # (в переменной series они хранились в кортежах)
            max_series += elem[0]  # высчитываем верхнюю границу - сумма всех серий во всех сезонах
        users_series = max_series // 2  # первый элемент в бинарном поиске - максимум / 2. делим без остатка

        self.vk.messages.send(user_id=user,  # задаем первый вопрос, нашу точку отсчета
                              message=str(
                                  self.cur.execute(f"SELECT Вопрос from '{name}' where id = {users_series}").fetchall()[
                                      0][
                                      0]),
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=self.search_keyboard.get_keyboard())

        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.obj.message['text'].lower() == 'вспомнилось!':  # функция, если пользователь вспомнил всё,
                    # что хотел, и ему нужно узнать серию
                    seria_name = str(
                        self.cur.execute(f"SELECT Серия from '{name}' where id = {users_series}").fetchall()[0][
                            0])  # узнаем имя серии
                    self.remembr(users_series, seasons, users_season, seria_name, event.obj.message['from_id'])
                elif event.obj.message['text'].lower() == 'да':
                    min_seires = users_series  # если пользователь ответил да, мы сдвигаем нижнюю границу
                    users_series = min_seires + (max_series - min_seires) // 2  # вычисляем серию пользователя
                    if users_series == min_seires or users_series == max_series:  # проверяем, не дошел ли юзер до верхней
                        # или нижней границы
                        seria_name = str(
                            self.cur.execute(f"SELECT Серия from '{name}' where id = {users_series}").fetchall()[0][0])
                        self.remembr(users_series, seasons, users_season, seria_name, event.obj.message['from_id'])
                    self.vk.messages.send(user_id=event.obj.message['from_id'],  # если нет, задаем вопрос пользователю
                                          message=str(
                                              self.cur.execute(
                                                  f"SELECT Вопрос from '{name}' where id = {users_series}").fetchall()[
                                                  0][0]),
                                          random_id=random.randint(0, 2 ** 64),
                                          keyboard=self.search_keyboard.get_keyboard())
                elif event.obj.message['text'].lower() == 'нет':
                    max_series = users_series  # если пользователь ответил нет, мы сдвигаем верхнюю границу
                    users_series = min_seires + (max_series - min_seires) // 2
                    if users_series == 0:  # проверка, не дошли ли мы до нулевой серии,
                        # если да, то мы говорим, что мы на серии 1
                        seria_name = str(
                            self.cur.execute(f"SELECT Серия from '{name}' where id = 1").fetchall()[0][0])
                        self.remembr(1, seasons, users_season, seria_name, event.obj.message['from_id'])
                    elif users_series == min_seires or users_series == max_series:  # снова проверка на границы
                        seria_name = str(
                            self.cur.execute(f"SELECT Серия from '{name}' where id = {users_series}").fetchall()[0][0])
                        self.remembr(users_series, seasons, users_season, seria_name, event.obj.message['from_id'])
                    self.vk.messages.send(user_id=event.obj.message['from_id'],  # если все хорошо, мы передаем вопрос
                                          message=str(
                                              self.cur.execute(
                                                  f"SELECT Вопрос from '{name}' where id = {users_series}").fetchall()[
                                                  0][0]),
                                          random_id=random.randint(0, 2 ** 64),
                                          keyboard=self.search_keyboard.get_keyboard())
                elif event.obj.message[
                    'text'].lower() == 'отмена':  # если пользователь нажал отмена, мы передаем параметры,
                    # среди которых идентификатор - вместо параметра seriales пустая строка
                    self.remembr(0, [], 0, "пустая строка", event.obj.message['from_id'])

    def remembr(self, users_series, seasons, users_season, name,
                id):  # функция для отправки пользователю сообщения о серии на которой он остановился. id серии,
        # список сезонов, сезон пользователя, имя серии и id пользователя

        if seasons:  # seasons - параметр-идентификатор, по нему мы определяем нажал пользователь отмена
            # или мы должны сообщить ему серию
            while users_series > seasons[
                users_season]:  # цикл для вычисления сезона на котором остановился пользователь
                # и серии(до этого серии могут иметь номер, например, 128, когда в сезоне всего 15 серий)
                users_series -= seasons[users_season]
                users_season += 1
            self.vk.messages.send(user_id=id,
                                  message="Поздравляю, ты остановился на серии " + name + " - " + str(
                                      users_series) + " серии " + str(
                                      users_season + 1) + " сезона",
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.keyboard.get_keyboard())
        else:  # это если пользователь нажал отмена
            self.vk.messages.send(user_id=id,
                                  message="*звук закрывающейся папки и вздох*",
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.keyboard.get_keyboard())
        self.main()  # снова запускаем основную функцию

    def sql_fetch(self):  # функция для определения, есть ли спрашиваемый пользователем сериал в бд.
        # для более полного объяснения смотрите файл READ_ME, пометка 1
        result = self.cur.execute('SELECT name from sqlite_master where type= "table"').fetchall()
        names = []
        for elem in result:
            names.append(elem[0])
        return names



if __name__ == '__main__':
    bot = Bot()
    bot.main()
