import QIWI_API
import telebot
from telebot import types
from decimal import Decimal

# Инициализация бота
Bot = telebot.TeleBot('5293129292:AAFLb6IJl8XThYWUH4DpFrn7bZ4En-Noy_8')
LoginMode = False
Regestration_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Regestration_markup.add(types.KeyboardButton("Регистрация"))

Delete_markup = types.ReplyKeyboardRemove()

Main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Main_menu_markup.add(types.KeyboardButton("Создать ссылку на пополнение Steam"))
Main_menu_markup.add(types.KeyboardButton("Подтвердить статус оплаты"))
Main_menu_markup.add(types.KeyboardButton("Менеджер акаунтов"))

Nick_Name_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Nick_Name_menu_markup.add(types.KeyboardButton("Добавить акаунт Steam"))
Nick_Name_menu_markup.add(types.KeyboardButton("Сменить Steam акаунт"))
Nick_Name_menu_markup.add(types.KeyboardButton("Назад"))

Order_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Order_menu_markup.add(types.KeyboardButton("Назад"))

Change_Nick_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Change_Nick_menu_markup.add(types.KeyboardButton("Назад"))

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
        Bot.send_message(message.chat.id, 'Бип ? Буп !\nБот перезагружен', reply_markup= Regestration_markup)

def NickNameMenu(message):
    if("Добавить акаунт Steam" == message.text):
        print("Запрос регестрации: "+str(message.chat.id))
        Bot.send_message(message.chat.id, 'Пожалуйста введите свой логин в Steam\nОн расположен в окне Steam во вкладке с верху с права',reply_markup = Change_Nick_menu_markup)
        login_tip_img = open('Logintip.png','rb')
        Bot.send_photo(message.chat.id,login_tip_img)
        Bot.register_next_step_handler(message,Add_Steam)
        #nisk_respons_SQL = QIWI_API.Check_Customer(Connection,message.chat.id)
        #nick_name = nisk_respons_SQL['data'][0][0]
        #print('m'+nick_name)
        #respons_SQL = QIWI_API.Off_Customer(Connection,message.chat.id,nick_name)
        #if respons_SQL['successfully']:
        #    Bot.send_message(message.chat.id, 'Ваш ник отвязан\nВы можете зарегестрироваться под новым', reply_markup= Regestration_markup)
        #    Bot.register_next_step_handler(message,start)

    if("Сменить Steam акаунт" == message.text):
        respons_SQL = QIWI_API.Get_NickNames(Connection,message.chat.id)
        if respons_SQL['successfully']:
            Bot.send_message(message.chat.id, 'Список акаунтов Steam')
            coutn_rows = 1
            for rows in respons_SQL['data']:
                nick_name = rows[0]
                if rows[1] == '1':
                    logined = 'Текущий'
                else:
                    logined = ''
                Bot.send_message(message.chat.id, str(coutn_rows)+'. '+nick_name+' '+logined)
                coutn_rows += 1
            Bot.send_message(message.chat.id, 'Введите Steam акаунт на который хотите переключиться',reply_markup = Change_Nick_menu_markup)
            Bot.register_next_step_handler(message, ChangeNickName)

        
    if("Назад" == message.text):
        Bot.send_message(message.chat.id, 'Выберите действие',reply_markup= Main_menu_markup)
        Bot.register_next_step_handler(message,main)

def ChangeNickName(message):
    nisk_respons_SQL = QIWI_API.Check_Customer(Connection,message.chat.id)
    nick_name = nisk_respons_SQL['data'][0][0]
    print('C'+nick_name)
    if("Назад" == message.text):
        Bot.send_message(message.chat.id, 'Ваш текущий ник: '+nick_name,reply_markup= Nick_Name_menu_markup)
        Bot.register_next_step_handler(message,NickNameMenu)
    else:
        finded = False;
        respons_SQL = QIWI_API.Get_NickNames(Connection,message.chat.id)
        for rows in respons_SQL['data']:
                nick_name = rows[0]
                if nick_name == message.text:
                    finded = True
                    respons_SQL = QIWI_API.Set_default_Nick(Connection,nick_name,message.chat.id)
                    if respons_SQL['successfully']:
                       Bot.send_message(message.chat.id, 'Выпереключены на Steam '+nick_name,reply_markup= Nick_Name_menu_markup) 
                       Bot.register_next_step_handler(message, NickNameMenu)
        if not finded:
            Bot.send_message(message.chat.id, 'Такой Steam не найден '+message.text,reply_markup= Change_Nick_menu_markup) 
            Bot.register_next_step_handler(message, ChangeNickName)



def main(message):
    nisk_respons_SQL = QIWI_API.Check_Customer(Connection,message.chat.id)
    if nisk_respons_SQL['successfully'] and nisk_respons_SQL['data']:
        nick_name = nisk_respons_SQL['data'][0][0]
        print(nick_name)
        if "Создать ссылку на пополнение Steam" == message.text:               
            Bot.send_message(message.chat.id, 'Введите сумму на котору пополнить акаунт\n'+nick_name+'\nМинимум 20р',reply_markup = Order_menu_markup)
            Bot.register_next_step_handler(message,createpayment)
            
        if "Подтвердить статус оплаты" == message.text:
            respons_QIWI = QIWI_API.Find_paid_order(Connection, QIWI_API.Token, QIWI_API.SecretKey, nick_name, message.chat.id)
            if respons_QIWI['successfully'] and respons_QIWI['data']:
                Bot.send_message(message.chat.id, 'Подтверждено\n'+respons_QIWI['data']['PAID']+' пополненией\n'+respons_QIWI['data']['COMPLETED']+' заказов отправлено на Steam',reply_markup= Main_menu_markup)
                Bot.register_next_step_handler(message,main)
            else:
                Bot.send_message(message.chat.id, 'Оплат по ссылкам не найдено !',reply_markup= Main_menu_markup)
                Bot.register_next_step_handler(message,main)
            
        if "Менеджер акаунтов" == message.text:
            Bot.send_message(message.chat.id, 'Ваш текущий ник: '+nick_name,reply_markup= Nick_Name_menu_markup)
            Bot.register_next_step_handler(message,NickNameMenu)
    else:
        print('У клиента ошибка ! '+str(message.chat.id))
        Bot.send_message(message.chat.id, 'Ошибка!/nВаш ник не найден/nПовторите попытку или свяжитесь с подержкой!')
        Bot.register_next_step_handler(message,main)

def createpayment(message):
    if("Назад" == message.text):
        Bot.send_message(message.chat.id, 'Выберите действие',reply_markup= Main_menu_markup)
        Bot.register_next_step_handler(message,main)
    else:   
        if message.text.isdigit():
            amount_Dec = round(Decimal(message.text),2)
            if amount_Dec >= round(Decimal('20'),2):
                Bot.send_message(message.chat.id, 'Создание ссылки для оплаты')
                respons_SQL = QIWI_API.Check_Customer(Connection,message.chat.id)
                if respons_SQL['successfully'] and respons_SQL['data']:
                    nick_name = respons_SQL['data'][0][0]
                    respons_SQL = QIWI_API.Create_order(Connection, QIWI_API.SecretKey,message.text,'Account replenishment',nick_name)
                    if respons_SQL['successfully'] and respons_SQL['data']:
                        order_URL = respons_SQL['data']
                        Bot.send_message(message.chat.id, 'После оплаты нажмите на "Подтвердить статус оплаты"\nВаша ссылка для оплаты:\n'+order_URL,reply_markup= Main_menu_markup)
                        Bot.register_next_step_handler(message,main)
                    else:
                        print('У клиента ошибка ! '+str(message.chat.id)+'\nСсылка на заказ не создана')
                        Bot.send_message(message.chat.id, 'Ошибка!\nСсылка не создана\nПовторите попытку или свяжитесь с подержкой!',reply_markup= Main_menu_markup)
                        Bot.register_next_step_handler(message,main)
                else:
                    print('У клиента ошибка ! '+str(message.chat.id)+'\nНе найден ник при создании заказа')
                    Bot.send_message(message.chat.id, 'Ошибка!\nВаш ник не найден\nПовторите попытку или свяжитесь с подержкой!',reply_markup = Main_menu_markup)
                    Bot.register_next_step_handler(message,main)
            else:
                Bot.send_message(message.chat.id, 'Платеж должен составлять минимум 20',reply_markup = Order_menu_markup)
                Bot.register_next_step_handler(message,createpayment)
        else:
            Bot.send_message(message.chat.id, 'Используйте только цифры',reply_markup = Order_menu_markup)
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
        Bot.send_message(message.chat.id, 'На ваш акаунт зарегестрирован ник: '+message.text+'\nДля начала попробуйте произвести минимальный платеж',reply_markup = Main_menu_markup)
        Bot.register_next_step_handler(message,main)
    else:
        Bot.send_message(message.chat.id, 'Ошибка при регестрации, повторите попытку или свяжитесь с подержкой!')
        Bot.register_next_step_handler(message,start)

def Add_Steam(message):
    if("Назад" == message.text):
        Bot.send_message(message.chat.id, 'Выберите действие',reply_markup= Nick_Name_menu_markup)
        Bot.register_next_step_handler(message,NickNameMenu)
    else:
        respons_SQL = QIWI_API.Create_customer(Connection,message.chat.id,message.text)
        if respons_SQL['successfully']:
            QIWI_API.Set_default_Nick(Connection,message.text,message.chat.id)
            Bot.send_message(message.chat.id, 'На ваш акаунт зарегестрирован ник: '+message.text+'\nОн выбран основным',reply_markup = Main_menu_markup)
            Bot.register_next_step_handler(message,main)
        else:
            Bot.send_message(message.chat.id, 'Ошибка при регестрации, повторите попытку или свяжитесь с подержкой!')
            Bot.register_next_step_handler(message,start)


# Запускаем бота
Connection = QIWI_API.Create_SQL_connection(QIWI_API.SQLHostName,QIWI_API.SQLUserName,QIWI_API.SQLRassword,QIWI_API.SQLBaseName)
print("Старт:\n"+str(Bot.get_me()))
Bot.polling(none_stop=True, interval=0)
print("Is Stop")
