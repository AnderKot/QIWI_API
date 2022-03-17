import requests
import mysql.connector
from mysql.connector import Error

Token = 'e4460425fb33c497219a74b6a4318d38'
Login = '79885028775'

SQLHostName = '192.168.1.101'
SQLUserName = 'Ander_kot'
SQLRassword = 'vfvf2009'
# Профиль пользователя
def get_profile(api_access_token):
    s7 = requests.Session()
    s7.headers['Accept']= 'application/json'
    s7.headers['authorization'] = 'Bearer '+ api_access_token
    p = s7.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true')
    return p.json()

# Баланс QIWI Кошелька
def balance(login, api_access_token):
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
def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL подключен")
    except Error as e:
        print(f"Ошибка подключения к MySQL '{e}'")
        
print(payment_history_last(Login,Token,10))
