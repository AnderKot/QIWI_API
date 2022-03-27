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

SQLHostName = '192.168.1.101'
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
def Get_balance(connection,login, api_access_token):
    s = requests.Session()
    s.headers['Accept']= 'application/json'
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    respons = s.get('https://edge.qiwi.com/funding-sources/v2/persons/' + login + '/accounts')
    if respons.ok:
        respons_Json = respons.json()
        query = "UPDATE wallet SET Amount = "+str(respons_Json['accounts'][0]['balance']['amount'])+" WHERE Name = 'qw_wallet_rub';"
        if execute_query(connection,query,'Баланс РУБ '+str(respons_Json['accounts'][0]['balance']['amount'])):
            query = "UPDATE wallet SET Amount = "+str(respons_Json['accounts'][1]['balance']['amount'])+" WHERE Name = 'qw_wallet_kzt';"
            if execute_query(connection,query,'Баланс КЗТ '+str(respons_Json['accounts'][1]['balance']['amount'])):
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
        return {'successfully':False, 'data':''}
        

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
        print("MySQL подключен")
    except Error as e:
        print(f"Ошибка подключения к MySQL '{e}'")
    return connection

# Отправка запроса SQL
def execute_query(connection, query, tip='не определено'):
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
def Create_customer(connection,Tg_ID, nick_name):
    create_query = "INSERT INTO customers VALUES ("+str(Tg_ID)+",'"+nick_name+"',0,0,1);"
    return execute_query(connection,create_query,'Создание клиента '+nick_name)
    
# Проверка акаунта
def Check_Customer(connection,tg_ID):
    create_query = "SELECT NickName,RU,KZ FROM customers WHERE TgID = "+str(tg_ID)+" AND Logined = 1;"
    return execute_query(connection,create_query,'данные клиента '+str(tg_ID))

# Отключение акаунта
def Off_Customer(connection,tg_ID,nick_Name):
    create_query = "UPDATE customers SET Logined = 0  WHERE TgID = "+str(tg_ID)+" AND NickName = '"+nick_Name+"';"
    return execute_query(connection,create_query,'Отказ от ника '+nick_Name+': '+str(tg_ID))
    
# Коммиссия
def Get_Commission(connection):
    create_query = "SELECT commission FROM config;"
    respons_SQL = execute_query(connection,create_query,'коммиссию')
    if respons_SQL['successfully'] and respons_SQL['data']: 
        сommission = respons_SQL['data'][0][0]
        return {'successfully':True, 'data':сommission}
    else:
        return {'successfully':False, 'data':''}
 
# Создание заказа
def Create_order(connection, api_secret_token, amount, comment, nick_name):
    datetime_str = str(datetime.datetime.now().isoformat())
    print(api_secret_token)
    # Запрос коммиссии
    respons_SQL = Get_Commission(connection)
    if respons_SQL['successfully'] and respons_SQL['data']:
        commission = respons_SQL['data']
        amount_decimal = Decimal(amount)
        commission_decimal = Decimal(commission)/Decimal(100)+Decimal(1)
        amount_str = str(round(amount_decimal*commission_decimal,2))
        # Создание заказа в QSL
        query = "INSERT INTO orders(NickName,RU,CreateDateTime) VALUES ('"+nick_name+"',"+amount_str+",'"+datetime_str+"');"
        respons_SQL = execute_query(connection,query,'Создание pаказа для '+nick_name)
        if respons_SQL['successfully']:
            query = "SELECT MAX(No) FROM orders;"
            respons_SQL = execute_query(connection,query,'Сбор ID pаказа')
            if respons_SQL['successfully']:
                order_ID = respons_SQL['data'][0][0]
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
                    respons_SQL = Check_Oreder(connection, api_secret_token,order_ID)
                    if respons_SQL['successfully'] and respons_SQL['data'] == 'WAITING': 
                        respons_Json = respons.json()
                        url = str(respons_Json['payUrl'])
                        print(url)
                        respons_SQL = Add_URL(connection,url,order_ID)
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
    else:
        return {'successfully':False, 'data':''}

# Обновление статуса заказа
def Check_Oreder(connection, api_secret_token, order_ID):
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
        if execute_query(connection,query,'Обновление pаказа '+status+'|'+'ID'):
            return {'successfully':True, 'data':status}
        else:
            {'successfully':False, 'data':''}
    return {'successfully':False, 'data':''}

# Исполнение оплаченых заказов
def Find_paid_order(connection, api_access_token, api_secret_token,nickName,tg_ID):
    # Обновление статусов заказов ожидающих оплату
    query = "SELECT No FROM orders WHERE NickName = '"+nickName+"' AND Status = 'WAITING';"
    respons_SQL = execute_query(connection,query,'Отбор заказов на подтверждение '+nickName)
    print(str(respons_SQL['data']))
    if respons_SQL['successfully'] and respons_SQL['data']:
        for rows in respons_SQL['data']:          
            Check_Oreder(connection,api_secret_token,rows[0])
    # Обновление статусов заказов ожидающих конвертацию в Тенге     
    query = "SELECT No,RU FROM orders WHERE NickName = '"+nickName+"' AND Status = 'PAID';"
    respons_SQL = execute_query(connection,query,'Отбор заказов на конвертацию '+nickName)
    if respons_SQL['successfully'] and respons_SQL['data']:
        for rows in respons_SQL['data']:
            order_ID_str = rows[0]
            cross = Decimal(Get_Cross_Rates(api_access_token))
            amount_RUB = Decimal(rows[1])
            amount_KZT = amount_RUB/cross
            amount_KZT_str = str(round(amount_KZT,2))
            respons_API = Convert(api_access_token,order_ID_str,amount_KZT_str)
            if respons_API['successfully']:
                Set_crossed(connection,order_ID,nickName,amount_KZT_str,tg_ID)
    # Обновление статусов заказов ожидающих исполнение
    query = "SELECT No,KZ FROM orders WHERE NickName = '"+nickName+"' AND Status = 'CROSSED';"
    respons_SQL = execute_query(connection,query,'Отбор заказов на конвертацию '+nickName)
    if respons_SQL['successfully'] and respons_SQL['data']:
        for rows in respons_SQL['data']:
            order_ID = rows[0]
            amount_KZT = round(Decimal(rows[1]),2)
            Send_To_Steam(api_access_token,nickName,amount_KZT,order_ID)
    else:
        return {'successfully':False, 'data':''}
        
# Установка баланса по умолчанию
def Set_default_wallet(connection, login, api_access_token, wallet):
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
        if execute_query(connection,query,'Обнуление статуса кошельков'):
            query = "UPDATE wallet SET Is_default = 1 WHERE Name = '"+wallet+"';"
            if execute_query(connection,query,'Установка стандартного кошелька: '+wallet):
                return {'successfully':True, 'data':''}
    return {'successfully':False, 'data':''}

# Добавить Url к заказу
def Add_URL(connection,order_URL,order_ID):
    order_ID_str = str(order_ID)
    query = "UPDATE orders SET Url = '"+order_URL+"' WHERE No = "+order_ID_str+";"
    respons_SQL = execute_query(connection,query,'Установка URL заказу '+str(order_ID)+': '+str(order_URL))
    if respons_SQL['successfully']:
        return {'successfully':True, 'data':''}
    else:
        return {'successfully':False, 'data':''}

# Добавить KZT на акаунт и заказ, перевести заказ в "CROSSED"
def Set_crossed(connection,order_ID,nickName,amount_KZT,tg_ID):
    order_ID_str = str(order_ID)
    # query = "SELECT KZ FROM customers WHERE No = "+order_ID_str+";"
    query = "UPDATE orders SET KZ = "+amount_KZT+",Status = 'CROSSED' WHERE No = "+order_ID_str+";"
    respons_SQL = execute_query(connection,query,'Подтверждение перевода '+amount_KZT+' Тенге на '+order_ID_str)
    query = "UPDATE customers SET KZ = KZ + "+amount_KZT+" WHERE NickName = '"+nickName+"' AND TgID = "+tg_ID+";"
    respons_SQL = execute_query(connection,query,'Запись на счет '+nickName+' '+amount_KZT+' Тенге')
    
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
    print(str(json_API))
    respons = requests.post(url, headers=headers_API, json=json_API)

    print(str(respons))
    print(str(respons.text))
    
# print(payment_history_last(Login,Token,10))
Connection = Create_SQL_connection(SQLHostName,SQLUserName,SQLRassword,SQLBaseName)
# Find_paid_order(Connection,Token,SecretKey,'ander_kot','777411561')
# print(get_balance(Login,Token))
# Check_Oreder(Connection,SecretKey,9)
# create_customer(Connection,'TEST01')
# Set_default_wallet(Connection,Login,Token,'qw_wallet_kzt')
# get_balance(Connection,Login,Token)
#  print(str(Get_Cross_Rates(Token)))
#  Convert(Token,80)
# print(str(Create_order(Connection,SecretKey,11,'Test','lj')))
Send_To_Steam(Token,'Ander_kot', round(Decimal(613.54),2),'29')
# print(create_order(Connection,SecretKye,1,'Test paid','Ander_kot'))
