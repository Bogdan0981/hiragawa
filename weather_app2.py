import streamlit as st
import psycopg2
import requests
from datetime import datetime, timedelta
import json


# проверка подключения к инету
def check_connection():
    try:
        requests.get('http://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False
    

# подключение к бд
def connect_db():
    return psycopg2.connect (
        dbname = 'postgres',
        user = 'postgres',
        password = 'kb0904',
        host = 'localhost',
        port = '5433'
    )
# функция connect_db возвращает обьект, котороый находиться в бд, то есть у нас есть все таблицы из бд

# получение данных текущей погоды с OpenWeather
def get_current_weather(city):
    api_key = '2624fd25b511ea7d85afbcb3f9439698'
    response = requests.get(url=f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric")
    if response.status_code == 200:
        return response.json()
    else:
        return None

# получение данных прогноза погоды с OpenWeather
def get_forecast(city):
    api_key = '2624fd25b511ea7d85afbcb3f9439698'
    response = requests.get(url=f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric")
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

# получение данных из бд
def get_current_weather_from_db(city):
    with connect_db() as con:
        with con.cursor() as cur:
            cur.execute('SELECT record_time, temperature, humidity, cloudiness, wind_speed, city_name FROM current_weather WHERE city_name = %s ORDER BY record_time DESC LIMIT 1', (city,))
            data = cur.fetchone()
            if data:
                return{
                    'name': city,
                    'main': {
                        'temp': data[1],
                        'humidity': data[2]
                    },
                    'clouds': {
                        'all': data[3],
                    },
                    'wind': {
                        'speed': data[4],
                    }
                }
            else:
                return None
            
# получение прогноза погоды из бд
def get_forecast_from_db(city):
    with connect_db() as con:
        with con.cursor() as cur:
            cur.execute('SELECT date_time, temp_min, temp_max, humidity, cloudiness, wind_speed, city_name FROM forecast WHERE city_name = %s', (city,))
            data = cur.fetchone()
            if data and data[0]:
                forecast_data = data[0]
                if isinstance(forecast_data, str):
                    try:
                        return json.loads(forecast_data)
                    except json.JSONDecodeError as e:
                        print(f'Ошибка декодирования данных прогноза погоды: {e}')
                else:
                    print(f'Ожидались данные в формате строки, получен тип {type(forecast_data)}')
                    return None
            else:
                return None 

print(get_forecast_from_db('London'))