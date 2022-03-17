import requests
import mysql.connector
from decimal import Decimal
import datetime
from datetime import timedelta
from mysql.connector import Error
from requests.structures import CaseInsensitiveDict

Token = 'e4460425fb33c497219a74b6a4318d38'
Login = '79885028775'
SecretKye = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6IjY2MnI2eC0wMCIsInVzZXJfaWQiOiI3OTg4NTAyODc3NSIsInNlY3JldCI6ImJiMTBlMDk3NzYyNjhiMTRmOGMzYzFhYzZlMzQ4MzkwNTUyNjY0Mjk3YTZiNjU0MWU5YmVhODQ4M2ZkZjliMzEifX0='

SQLHostName = '192.168.1.101'
SQLUserName = 'Ander_kot'
SQLRassword = 'vfvf2009'
SQLBaseName = 'myqiwisql'

# Профиль пользователя
def get_profile(api_access_token):
    s7 = requests.Session()
    s7.headers['Accept']= 'application/json'
    s7.headers['authorization'] = 'Bearer '+ api_access_token
    p = s7.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true')
    return p.json()

# Баланс QIWI Кошелька
def get_balance(login, api_access_token):
    s = requests.Session()
    s.headers['Accept']= 'application/json'
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    b = s.get('https://edge.qiwi.com/funding-sources/v2/persons/' + login + '/accounts')
    return b.json()

# История платежей - последние n платежей
def payment_history_last(login, api_access_token, rows_num):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    parameters = {'rows': rows_num, 'operation': 'IN'}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + login + '/payments', params = parameters)
    return h.json()

# Подключение к серверу SQL
def create_SQL_connection(host_name, user_name, user_password, db_name):
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
        connection.commit()
        print('Запрос на '+tip+' отправлен')
        return True
    except Error as e:
        print(f"Ошибка в запросе '{e}'")
        return False
         
# Создание клиента
def create_customer(connection, nick_name):
    create_query = "INSERT INTO customers VALUES ('"+nick_name+"',0,0);"
    return execute_query(connection,create_query,'Создание клиента '+nick_name)
    
    
# Создание заказа
def create_order(connection, api_access_token, amount, comment, nick_name):
    amount_str = str(Decimal(amount))
    datetime_str = str(datetime.datetime.now().isoformat())
    # SQL ---
    query = "INSERT INTO orders(NickName,RU,CreateDateTime,Status) VALUES ('"+nick_name+"',"+amount_str+",'"+datetime_str+"','Create');"
    print(query)
    if execute_query(connection,query,'Создание pаказа '+nick_name+'|'+'ID'):
        # API ---
        url = "https://api.qiwi.com/partner/bill/v1/bills/"+str(12)
        end_datetime = datetime.date.today() + datetime.timedelta(1)
        # Заголовок
        headers_API = CaseInsensitiveDict()
        headers_API["content-type"] = "application/json"
        headers_API["accept"] = "application/json"
        headers_API["Authorization"] = "Bearer " + api_access_token
        # Данные
        json_API = '''
        {
           "amount": {
             "currency": "RUB",
             "value": "1.00"
           },
           "comment": "Test nick: '''+str(nick_name)+'''",
           "expirationDateTime": "'''+str(end_datetime.isoformat())+'''T12:00:00+03:00",
            "customer": {
                "phone": null,
                "email": null,
                "account": "'''+str(nick_name)+'''"
           }, 
           "customFields" : {
                "paySourcesFilter":null,
                "themeCode": null,
                "yourParam1": null,
                "yourParam2": null
            }
        }'''
        respons = requests.put(url, headers=headers_API, data=json_API)
        if respons.ok:
            return respons.json()
        return respons
    return False
    # create_query = "INSERT INTO orders VALUES ('"+nick_name+"',0,0);"      '''+str(end_datetime.isoformat())+'''
    # return execute_query(connection,create_query,'Создание клиента '+nick_name)

# Запрос данных клиента

# Запрос статуса заказа
# print(payment_history_last(Login,Token,10))
Connection = create_SQL_connection(SQLHostName,SQLUserName,SQLRassword,SQLBaseName);

# create_customer(Connection,'TEST01')

print(create_order(Connection,SecretKye,1,'Test paid','Ander_kot'))
