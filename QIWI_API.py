import requests
import mysql.connector
import json
import datetime
from datetime import timedelta
from mysql.connector import Error
from decimal import Decimal
from requests.structures import CaseInsensitiveDict

Token = 'e4460425fb33c497219a74b6a4318d38'
Login = '79885028775'
SecretKey = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6IjY2MnI2eC0wMCIsInVzZXJfaWQiOiI3OTg4NTAyODc3NSIsInNlY3JldCI6ImU4MDNlNGYyZmQ5ZmJjMzJhNTQxYjY5YjVlNjg2YTM0NTllMjc5YzM3MjVkNzA3MzE2NTc0NTczZjIzZThhMTIifX0='

SQLHostName = '127.0.0.1' # 192.168.1.101
SQLUserName = 'Ander_kot'
SQLRassword = 'vfvf2009'
SQLBaseName = 'myqiwisql'

# Профиль пользователя --
def get_profile(api_access_token):
    s7 = requests.Session()
    s7.headers['Accept']= 'application/json'
    s7.headers['authorization'] = 'Bearer '+ api_access_token
    p = s7.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true')
    return p.json()

# Баланс QIWI Кошелька --
def Get_balance(login, api_access_token):
    s = requests.Session()
    s.headers['Accept']= 'application/json'
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    respons = s.get('https://edge.qiwi.com/funding-sources/v2/persons/' + login + '/accounts')
    if respons.ok:
        respons_Json = respons.json()
        query = "UPDATE wallet SET Amount = "+str(respons_Json['accounts'][0]['balance']['amount'])+" WHERE Name = 'qw_wallet_rub';"
        if execute_query(query,'Баланс РУБ '+str(respons_Json['accounts'][0]['balance']['amount'])):
            query = "UPDATE wallet SET Amount = "+str(respons_Json['accounts'][1]['balance']['amount'])+" WHERE Name = 'qw_wallet_kzt';"
            if execute_query(query,'Баланс КЗТ '+str(respons_Json['accounts'][1]['balance']['amount'])):
                return True
    return False

# Курс валют
def Get_Cross_Rates(api_access_token):
    # API ---
    url = "https://edge.qiwi.com/sinap/crossRates"
    # Заголовок
    headers_API = CaseInsensitiveDict()
    headers_API["content-type"] = "application/json"
    headers_API["accept"] = "application/json"
    headers_API["Authorization"] = "Bearer " + api_access_token
    respons = requests.get(url, headers=headers_API)
    respons_Json = respons.json()
    cross = str(respons_Json['result'][6]['rate'])
    return cross

# Конвертация валют
def Convert(api_access_token,order_ID,amount):
    # API ---
    url = "https://edge.qiwi.com/sinap/api/v2/terms/1099/payments"
    # Заголовок
    headers_API = CaseInsensitiveDict()
    headers_API["content-type"] = "application/json"
    headers_API["accept"] = "application/json"
    headers_API["Authorization"] = "Bearer " + api_access_token
    post_json = {"id":"","sum":{"amount":"","currency":"398"},"paymentMethod":{"type":"Account","accountId":"643"}, "Convert ty KZT":"TEST","fields":{"account":"+79885028775"}}
    post_json['id'] = str(order_ID)
    post_json['sum']['amount'] = str(amount)
    respons = requests.post(url, headers=headers_API, json=post_json)
    if respons.ok:
        return {'successfully':True, 'data':''}
    else:
        return {'successfully':False, 'data':respons.text}
        

# Последние n платежей --
def payment_history_last(login, api_access_token, rows_num):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    parameters = {'rows': rows_num, 'operation': 'IN'}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + login + '/payments', params = parameters)
    return h.json()

# Подключение к серверу SQL --
def Create_SQL_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name    
        )
    except Error as e:
        print(f"Ошибка подключения к MySQL '{e}'")
    return connection

# Отправка запроса SQL
def execute_query(query, tip='не определено'):
    connection = Create_SQL_connection(SQLHostName,SQLUserName,SQLRassword,SQLBaseName)
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        connection.commit()
        print('Запрос на '+tip+' отправлен')
        return {'successfully':True, 'data':result}
    except Error as e:
        print(f"Ошибка в запросе '{e}'")
        return {'successfully':False, 'data':''}
         
# Создание клиента
def Create_customer(Tg_ID, nick_name):
    create_query = "INSERT INTO customers VALUES ("+str(Tg_ID)+",'"+nick_name+"',0,0,1);"
    respons_SQL = execute_query(create_query,'Создание клиента '+nick_name)
    return respons_SQL
    
# Проверка акаунта
def Check_Customer(tg_ID):
    create_query = "SELECT NickName,RU,KZ FROM customers WHERE TgID = "+str(tg_ID)+" AND Logined = 1;"
    respons_SQL = execute_query(create_query,'данные клиента '+str(tg_ID))
    return respons_SQL

# Отключение акаунта
def Off_Customer(tg_ID,nick_Name):
    connection = Create_SQL_connection(SQLHostName,SQLUserName,SQLRassword,SQLBaseName)
    create_query = "UPDATE customers SET Logined = 0  WHERE TgID = "+str(tg_ID)+" AND NickName = '"+nick_Name+"';"
    return execute_query(create_query,'Отказ от ника '+nick_Name+': '+str(tg_ID))
    
    
# Коммиссия
def Get_Commission():
    create_query = "SELECT commission FROM config;"
    respons_SQL = execute_query(create_query,'коммиссию')
    if respons_SQL['successfully'] and respons_SQL['data']: 
        сommission = respons_SQL['data'][0][0]
        return {'successfully':True, 'data':сommission}
    else:
        return {'successfully':False, 'data':''}
 
# Создание заказа
def Create_order(api_secret_token, amount, comment, nick_name):
    datetime_str = str(datetime.datetime.today().replace(microsecond=0).isoformat())
    print(datetime_str)
    print(api_secret_token)
    # Запрос коммиссии
    respons_SQL = Get_Commission()
    if respons_SQL['successfully'] and respons_SQL['data']:
        commission = respons_SQL['data']
        amount_decimal = Decimal(amount)
        commission_decimal = Decimal(commission)/Decimal(100)+Decimal(1)
        amount_str = str(round(amount_decimal*commission_decimal,2))
        # Создание заказа в QSL
        query = "SELECT MAX(No) FROM orders;"
        respons_SQL = execute_query(query,'Сбор ID заказа')
        order_ID = respons_SQL['data'][0][0]+5
        query = "INSERT INTO orders(No,NickName,RU,CreateDateTime) VALUES ("+str(order_ID)+",'"+nick_name+"',"+amount_str+",'"+datetime_str+"');"
        respons_SQL = execute_query(query,'Создание pаказа для '+nick_name)
        if respons_SQL['successfully']:
            # Создание заказа в QIWI API
            url = "https://api.qiwi.com/partner/bill/v1/bills/"+str(order_ID)
            end_datetime = datetime.date.today() + datetime.timedelta(1)
            # Заголовок
            headers_API = CaseInsensitiveDict()
            headers_API["content-type"] = "application/json"
            headers_API["accept"] = "application/json"
            headers_API["Authorization"] = "Bearer " + api_secret_token
            # Данные
            post_json = {"amount": {"currency": "RUB","value": ""},"comment": "","expirationDateTime": "","customer": {"phone": "","email": "","account": ""},"customFields" : {"paySourcesFilter":"","themeCode": "","yourParam1": "","yourParam2": ""}}
            post_json["amount"]["value"] = amount_str
            post_json["comment"] = comment+': '+str(nick_name)
            post_json["expirationDateTime"] = str(end_datetime.isoformat())+'T12:00:00+03:00'
            post_json["customer"]["account"] = str(nick_name)
            respons = requests.put(url, headers=headers_API, json=post_json)
            if respons.ok:
                respons_SQL = Check_Oreder(api_secret_token,order_ID)
                if respons_SQL['successfully'] and respons_SQL['data'] == 'WAITING': 
                    respons_Json = respons.json()
                    url = str(respons_Json['payUrl'])
                    print(url)
                    respons_SQL = Add_URL(url,order_ID)
                    if respons_SQL['successfully']:
                        return {'successfully':True, 'data':url}
                    else:
                        return {'successfully':False, 'data':''}
                else:
                    return {'successfully':False, 'data':''}
            else:
                return {'successfully':False, 'data':''}
        else:
            return {'successfully':False, 'data':''}
    else:
        return {'successfully':False, 'data':''}

# Обновление статуса заказа
def Check_Oreder(api_secret_token, order_ID):
    # API ---
    url = "https://api.qiwi.com/partner/bill/v1/bills/"+str(order_ID)
    headers_API = CaseInsensitiveDict()
    headers_API["content-type"] = "application/json"
    headers_API["accept"] = "application/json"
    headers_API["Authorization"] = "Bearer " + api_secret_token
    respons = requests.get(url, headers=headers_API)
    if respons.ok:
        respons_Json = respons.json()
        status = str(respons_Json['status']['value'])
        # SQL ---
        query = "UPDATE orders SET Status = '"+status+"' WHERE No = '"+str(order_ID)+"';"
        if execute_query(query,'Обновление pаказа '+status+'|'+str(order_ID)):
            return {'successfully':True, 'data':status}
        else:
            return {'successfully':False, 'data':''}
    return {'successfully':False, 'data':''}

# Список ников на акаунте
def Get_NickNames(tg_ID):
    tg_ID_str = str(tg_ID)
    query = "SELECT NickName,Logined FROM customers WHERE TgID = "+tg_ID_str+";"
    respons_SQL = execute_query(query,'список ников '+tg_ID_str)
    if respons_SQL['successfully'] and respons_SQL['data']:
        return {'successfully':True, 'data':respons_SQL['data']}
    else:
        return {'successfully':False, 'data':''}

# Исполнение оплаченых заказов
def Find_paid_order( api_access_token, api_secret_token,nickName,tg_ID):
    # Обновление статусов заказов ожидающих оплату
    query = "SELECT No FROM orders WHERE NickName = '"+nickName+"' AND Status = 'WAITING';"
    respons_SQL = execute_query(query,'Отбор заказов на подтверждение '+nickName)
    count_PAID_orders = 0
    if respons_SQL['successfully'] and respons_SQL['data']:
        for rows in respons_SQL['data']:          
            respons_API = Check_Oreder(api_secret_token,rows[0])
            if respons_API['successfully'] and (respons_API['data'] == 'PAID'):
                count_PAID_orders += 1
    # Обновление статусов заказов ожидающих конвертацию в Тенге     
    query = "SELECT No,RU FROM orders WHERE NickName = '"+nickName+"' AND Status = 'PAID';"
    respons_SQL = execute_query(query,'Отбор заказов на конвертацию '+nickName)
    count_CROSSED_orders = 0
    if respons_SQL['successfully'] and respons_SQL['data']:
        for rows in respons_SQL['data']:
            order_ID_str = rows[0]
            order_API_str = rows[0] + 1
            print(order_ID_str)
            print(order_API_str)
            cross = Decimal(Get_Cross_Rates(api_access_token))
            amount_RUB = Decimal(rows[1])
            amount_KZT = amount_RUB/cross
            amount_KZT_str = str(round(amount_KZT,2))
            respons_API = Convert(api_access_token,order_API_str,amount_KZT_str)
            print(str(respons_API['data']))
            if respons_API['successfully']:
                Set_crossed(order_ID_str,nickName,amount_KZT_str,tg_ID)
                count_CROSSED_orders += 1
    # Обновление статусов заказов ожидающих исполнение
    query = "SELECT No,KZ FROM orders WHERE NickName = '"+nickName+"' AND Status = 'CROSSED';"
    respons_SQL = execute_query(query,'Отбор заказов на исполнение '+nickName)
    count_COMPLETED_orders = 0
    if respons_SQL['successfully'] and respons_SQL['data']:
        for rows in respons_SQL['data']:
            order_ID = int(rows[0]) 
            order_ID_str = str(order_ID)
            order_Paid_ID = int(rows[0]) + 2
            order_Paid_ID_str = str(order_Paid_ID)
            print(order_ID_str)
            print(order_Paid_ID_str)
            amount_KZT = round(Decimal(rows[1]),2)
            amount_KZT_str = str(amount_KZT)
            respons_API = Send_To_Steam(api_access_token,nickName,amount_KZT,order_Paid_ID_str)
            if respons_API['successfully']:
                Set_comleted(order_ID_str,nickName,amount_KZT_str,tg_ID)
                count_COMPLETED_orders += 1
    if (count_PAID_orders + count_CROSSED_orders + count_COMPLETED_orders) > 0:
        return {'successfully':True, 'data':{"PAID":str(count_PAID_orders),"CROSSED":str(count_CROSSED_orders),"COMPLETED":str(count_COMPLETED_orders)}}
    else:
        return {'successfully':False, 'data':''}
        
# Установка баланса по умолчанию
def Set_default_wallet(login, api_access_token, wallet):
    url = "https://edge.qiwi.com/funding-sources/v2/persons/"+login+"/accounts/"+wallet
    headers_API = CaseInsensitiveDict()
    headers_API["content-type"] = "application/json"
    headers_API["accept"] = "application/json"
    headers_API["Authorization"] = "Bearer " + api_access_token
    data_API = '{ "defaultAccount": true }'
    respons_API = requests.patch(url, headers=headers_API, data=data_API)
    if respons_API.ok:
        # SQL ---
        query = "UPDATE wallet SET Is_default = 0;"
        if execute_query(query,'Обнуление статуса кошельков'):
            query = "UPDATE wallet SET Is_default = 1 WHERE Name = '"+wallet+"';"
            if execute_query(query,'Установка стандартного кошелька: '+wallet):
                return {'successfully':True, 'data':''}
    return {'successfully':False, 'data':''}

# Установка Steam акаунта по умолчанию
def Set_default_Nick(nickName,tg_ID ):
    tg_ID_str = str(tg_ID)
    query = "UPDATE customers SET Logined = 0 WHERE TgID = '"+tg_ID_str+"';"
    if execute_query(query,'Выключение Steam акаунтов '+tg_ID_str):
        query = "UPDATE customers SET Logined = 1 WHERE TgID = '"+tg_ID_str+"' AND NickName = '"+nickName+"';"
        if execute_query(query,'Включение Steam акаунта '+nickName+' клиенту ' +tg_ID_str):
            return {'successfully':True, 'data':''}
    return {'successfully':False, 'data':''}

# Добавить Url к заказу
def Add_URL(order_URL,order_ID):
    order_ID_str = str(order_ID)
    query = "UPDATE orders SET Url = '"+order_URL+"' WHERE No = "+order_ID_str+";"
    respons_SQL = execute_query(query,'Установка URL заказу '+str(order_ID)+': '+str(order_URL))
    if respons_SQL['successfully']:
        return {'successfully':True, 'data':''}
    else:
        return {'successfully':False, 'data':''}

# Добавить KZT на акаунт и заказ, перевести заказ в "CROSSED"
def Set_crossed(order_ID,nickName,amount_KZT,tg_ID):
    amount_KZT_str = str(amount_KZT) 
    tg_ID_str = str(tg_ID)
    order_ID_str = str(order_ID)
    # query = "SELECT KZ FROM customers WHERE No = "+order_ID_str+";"
    query = "UPDATE orders SET KZ = "+amount_KZT_str+",Status = 'CROSSED' WHERE No = "+order_ID_str+";"
    respons_SQL = execute_query(query,'Подтверждение перевода '+amount_KZT_str+' Тенге на '+order_ID_str)
    query = "UPDATE customers SET KZ = KZ + "+amount_KZT_str+" WHERE NickName = '"+nickName+"' AND TgID = "+tg_ID_str+";"
    respons_SQL = execute_query(query,'Запись на счет '+nickName+' '+amount_KZT_str+' Тенге')

# Убрать KZT с акаунта, перевести заказ в "COMPLETED"
def Set_comleted(order_ID,nickName,amount_KZT,tg_ID):
    amount_KZT_str = str(amount_KZT)
    print('1'+amount_KZT_str) 
    tg_ID_str = str(tg_ID)
    print('2'+tg_ID_str)
    datetime_str = str(datetime.datetime.now().isoformat())
    print('3'+datetime_str)
    order_ID_str = str(order_ID)
    print('4'+order_ID_str)
    query = "UPDATE customers SET KZ = KZ - "+amount_KZT_str+" WHERE NickName = '"+nickName+"' AND TgID = "+tg_ID_str+";"
    respons_SQL = execute_query(query,'списывание со счета '+nickName+' '+amount_KZT_str+' Тенге')
    query = "UPDATE orders SET PiadDateTime = '"+datetime_str+"', Status = 'COMPLETED' WHERE No = "+order_ID_str+";"
    respons_SQL = execute_query(query,'Завершение заказа')

# Перевод на стим 31212
def Send_To_Steam(api_access_token,nickName,amount_KZT,order_ID):
    amount_KZT_str = str(amount_KZT)
    url = "https://edge.qiwi.com/sinap/api/v2/terms/31212/payments"
    headers_API = CaseInsensitiveDict()
    headers_API["content-type"] = "application/json"
    headers_API["accept"] = "application/json"
    headers_API["Authorization"] = "Bearer " + api_access_token
    json_API = {"id":"","sum": {"amount":"","currency":"398"},"paymentMethod": {"type":"Account","accountId":"398"},"fields": {"account":""}}
    json_API['id'] = str(order_ID)
    json_API['sum']['amount'] = amount_KZT_str
    json_API['fields']['account'] = nickName
    respons = requests.post(url, headers=headers_API, json=json_API)

    if respons.ok:
        return {'successfully':True, 'data':''}
    else:
        return {'successfully':False, 'data':respons.text}
    
# print(payment_history_last(Login,Token,10))


# Set_comleted(Connection,'31','Ander_kot','100','777411561')
# Find_paid_order(Connection,Token,SecretKey,'Логинмой','187401430')
# print(get_balance(Login,Token))
# Check_Oreder(Connection,SecretKey,9)
# create_customer(Connection,'TEST01')
# Set_default_wallet(Connection,Login,Token,'qw_wallet_kzt')
# get_balance(Connection,Login,Token)
#  print(str(Get_Cross_Rates(Token)))
#  Convert(Token,80)
# print(str(Create_order(Connection,SecretKey,11,'Test','lj')))
# Send_To_Steam(Token,'Ander_kot', 613.54,'40')
# print(create_order(Connection,SecretKye,1,'Test paid','Ander_kot'))
# respons_API = Send_To_Steam(Token,'Логинмой','256.79','32')
# print(respons_API['data'])
# query = "UPDATE orders SET Status = 'CROSSED' WHERE No = 32;"
# respons_SQL = execute_query(Connection,query,'Запись на счет Тенге')
