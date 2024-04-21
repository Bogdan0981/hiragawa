import streamlit as st
import psycopg2
import requests
from datetime import datetime

# Функция для проверки подключения к интернету
def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="kb0904",
    host="localhost",
    port="5433"
)

# Создание курсора для работы с базой данных
cur = conn.cursor()

# Функция для получения данных о погоде из API OpenWeather
def get_weather_data_from_api(city):
    api_key = "ef4cfe7b51b74456e886d541c4c6bed4"  # Замени это на свой API ключ OpenWeather
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Функция для отображения главной страницы
def main_page():
    st.title("Приложение прогноза погоды")
    st.sidebar.title("Сайдбар")
    st.sidebar.write("Введите название города:")
    city_input = st.sidebar.text_input("Название города")
    if st.sidebar.button("Показать погоду"):
        if check_internet_connection():
            weather_data = get_weather_data_from_api(city_input)
            if weather_data:
                st.session_state.weather_data = weather_data
                st.rerun()
            else:
                st.error("Город не найден. Попробуйте еще раз или используйте сохраненные данные.")
        else:
            st.warning("Отсутствует подключение к интернету. Данные будут взяты из базы данных.")
            weather_data = get_weather_data_from_db(city_input)
            if weather_data:
                st.session_state.weather_data = weather_data
                st.rerun()
            else:
                st.error("Данные о погоде для данного города не найдены в базе данных.")

# Функция для отображения страницы погоды
def weather_page():
    st.title("Страница погоды")
    city_name = st.session_state.weather_data['name']
    st.write(f"Погода в городе {city_name}:", datetime.now().strftime('%H:%M:%S'))
    current_weather = st.session_state.weather_data['main']
    cloudiness = st.session_state.weather_data['clouds']
    wind = st.session_state.weather_data['wind']
    st.write("Текущая погода:")
    st.write(f"Температура: {current_weather['temp']}°C")
    st.write(f"Влажность: {current_weather['humidity']}")
    st.write(f"Облачность: {cloudiness['all']}")
    st.write(f"Скорость ветра: {wind['speed']}")
    
    # Отображение текущего времени
    

# Функция для получения данных о погоде из базы данных PostgreSQL
def get_weather_data_from_db(city):
    cur.execute("SELECT * FROM current_weather", (city,))
    data = cur.fetchone()
    if data:
        return {
            'record_time': data[0],
            'main': {
                'temperature': data[1],
                'humidity': data[2],
                'cloudiness': data[3],
                'wind_speed': data[4],
            }
        }
    else:
        return None

# Основной блок кода Streamlit
if 'weather_data' not in st.session_state:
    main_page()
else:
    weather_page()

# Закрытие соединения с базой данных
cur.close()
conn.close()
