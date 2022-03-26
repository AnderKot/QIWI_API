import QIWI_API
import telebot
from telebot import types

# Инициализация бота
Bot = telebot.TeleBot('5293129292:AAFLb6IJl8XThYWUH4DpFrn7bZ4En-Noy_8')
LoginMode = False
Regestration_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Regestration_markup.add(types.KeyboardButton("Регистрация"))

Delete_markup = types.ReplyKeyboardRemove()

Main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Main_menu_markup.add(types.KeyboardButton("Пополнить Steam"))

# Функция, обрабатывающая команду /start
@Bot.message_handler(commands=["start"])
def start(message, res=False):
    print(str(message.chat.id))
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    markup.add(types.KeyboardButton("Регистрация"))
    Bot.send_message(message.chat.id, 'Добро пожаловать!\nДля начала пройдите регистрацию', reply_markup= Regestration_markup)

# Функция, обработка сообщений
@Bot.message_handler(content_types=['text'])
def start(message):
    if "Регистрация" == message.text:
        respons_SQL = QIWI_API.Check_Customer(Connection,message.chat.id)
        if respons_SQL['successfully'] and respons_SQL['data']:
            nick_name = respons_SQL['data'][0][0]
            print('Клиент найден: '+nick_name)
            Bot.send_message(message.chat.id, 'Мы нашли ваш ник: '+nick_name+'\nОн будет использован по умолчанию',reply_markup= Main_menu_markup)
            Bot.register_next_step_handler(message,main)
        else:
            print("Запрос регестрации: "+str(message.chat.id))
            Bot.send_message(message.chat.id, 'Пожалуйста введите свой логин в Steam\nОн расположен в окне Steam во вкладке с верху с права',reply_markup = Delete_markup)
            login_tip_img = open('Logintip.png','rb')
            Bot.send_photo(message.chat.id,login_tip_img)
            Bot.register_next_step_handler(message,registration)
    else:
        Bot.send_message(message.chat.id, 'Бип ? Буп !', reply_markup= Regestration_markup)

def main(message):
    if "Пополнить Steam" == message.text:
        respons_SQL = QIWI_API.Check_Customer(Connection,message.chat.id)
        if respons_SQL['successfully'] and respons_SQL['data']:
            nick_name = respons_SQL['data'][0][0]
            Bot.send_message(message.chat.id, 'Введите сумму на котору пополнить '+nick_name,reply_markup = Delete_markup)
            Bot.register_next_step_handler(message,createpayment)
        else:
            print('У клиента ошибка ! '+str(message.chat.id))
            Bot.send_message(message.chat.id, 'Ошибка!/nВаш ник не найден/nПовторите попытку или свяжитесь с подержкой!')
            Bot.register_next_step_handler(message,start)

def createpayment(message):
    if message.text.isdigit():
        Bot.send_message(message.chat.id, 'Создание ссылки для оплаты')
        respons_SQL = QIWI_API.Check_Customer(Connection,message.chat.id)
        if respons_SQL['successfully'] and respons_SQL['data']:
            nick_name = respons_SQL['data'][0][0]
            respons_SQL = QIWI_API.Create_order(Connection, QIWI_API.SecretKey,message.text,'Account replenishment: ',nick_name)
            if respons_SQL['successfully'] and respons_SQL['data']:
                order_URL = respons_SQL['data']
                Bot.send_message(message.chat.id, 'Ваша ссылка для оплаты:\n'+order_URL)
                Bot.send_message(message.chat.id, 'Средства поступят на счет после оплаты')
                Bot.register_next_step_handler(message,main)
            else:
                print('У клиента ошибка ! '+str(message.chat.id)+'\nСсылка на заказ не создана')
                Bot.register_next_step_handler(message,main)
        else:
            print('У клиента ошибка ! '+str(message.chat.id)+'\nНе найден ник при создании заказа')
            Bot.send_message(message.chat.id, 'Ошибка!\nВаш ник не найден\nПовторите попытку или свяжитесь с подержкой!')
            Bot.register_next_step_handler(message,main)
    else:
        Bot.send_message(message.chat.id, 'Используйте только цифры !')
        Bot.register_next_step_handler(message,createpayment)
        
    
def end(message):
    end_img = open('Снимок экрана 2022-03-26 в 20.52.46.png','rb')
    print("клиент в конце")
    Bot.send_message(message.chat.id, 'Идет разработка )')
    Bot.send_photo(message.chat.id,end_img)
    Bot.register_next_step_handler(message,end)

def registration(message):
    respons_SQL = QIWI_API.Create_customer(Connection,message.chat.id,message.text)
    if respons_SQL['successfully']:
        Bot.send_message(message.chat.id, 'На ваш акаунт зарегестрирован ник: '+message.text,reply_markup = Main_menu_markup)
        Bot.register_next_step_handler(message,main)
    else:
        Bot.send_message(message.chat.id, 'Ошибка при регестрации, повторите попытку или свяжитесь с подержкой!')
        Bot.register_next_step_handler(message,start)


            
# Получение сообщений от юзера
# @Bot.message_handler(content_types=["text"])
# def handle_text(message):
#     print(str(message.chat.id))
#     Bot.send_message(message.chat.id, 'Вы написали: ' + message.text)

# Запускаем бота
Connection = QIWI_API.Create_SQL_connection(QIWI_API.SQLHostName,QIWI_API.SQLUserName,QIWI_API.SQLRassword,QIWI_API.SQLBaseName)
print("Старт:\n"+str(Bot.get_me()))
Bot.polling(none_stop=False, interval=0)
print("Is Stop")
