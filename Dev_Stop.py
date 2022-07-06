import QIWI_API
import telebot
import time
from telebot import types
from decimal import Decimal

# Инициализация бота
Bot = telebot.TeleBot('5293129292:AAFLb6IJl8XThYWUH4DpFrn7bZ4En-Noy_8')
LoginMode = False
Regestration_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Regestration_markup.add(types.KeyboardButton("Вход"))

Delete_markup = types.ReplyKeyboardRemove()

Main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Main_menu_markup.add(types.KeyboardButton("Создать ссылку на пополнение Steam"))
Main_menu_markup.add(types.KeyboardButton("Подтвердить статус оплаты"))
Main_menu_markup.add(types.KeyboardButton("Менеджер акаунтов"))

Nick_Name_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Nick_Name_menu_markup.add(types.KeyboardButton("Добавить новый акаунт Steam"))
Nick_Name_menu_markup.add(types.KeyboardButton("Сменить Steam акаунт"))
Nick_Name_menu_markup.add(types.KeyboardButton("Назад"))

Order_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Order_menu_markup.add(types.KeyboardButton("Назад"))

Change_Nick_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
Change_Nick_menu_markup.add(types.KeyboardButton("Назад"))

# Функция, обрабатывающая команду /start
@Bot.message_handler(commands=["start"])
def start(message, res=False):
    end_img = open('Снимок.PNG','rb')
    print("клиент в конце")
    Bot.send_message(message.chat.id, 'Идет разработка )')
    Bot.send_photo(message.chat.id,end_img)
    Bot.register_next_step_handler(message,end)

# Функция, обработка сообщений
@Bot.message_handler(content_types=['text'])
def end(message):
    end_img = open('Снимок.PNG','rb')
    print("клиент в конце")
    Bot.send_message(message.chat.id, 'Идет разработка )')
    Bot.send_photo(message.chat.id,end_img)
    Bot.register_next_step_handler(message,end)


# Запускаем бота
print("Старт:\n"+str(Bot.get_me()))
while True:
    try:
        Bot.polling(none_stop=True, interval=0)

    except Exception as e:
          # или просто print(e) если у вас логгера нет,
        # или import traceback; traceback.print_exc() для печати полной инфы
        time.sleep(500)

print("Is Stop")
