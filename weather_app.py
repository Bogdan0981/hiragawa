import streamlit as st
import psycopg2
import requests
from datetime import datetime, timedelta
import json

# Задание стилей

# Функция для проверки подключения к интернету
def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="kb0904",
        host="localhost",
        port="5433"
    )

# Функция для получения данных о погоде из API OpenWeather
def get_weather_data_from_api(city):
    api_key = "2624fd25b511ea7d85afbcb3f9439698"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Функция для получения прогноза погоды на 5 дней из API OpenWeather
def get_weather_forecast_from_api(city):
    api_key = "2624fd25b511ea7d85afbcb3f9439698"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Функция для получения данных о погоде из базы данных PostgreSQL
def get_weather_data_from_db(city):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT temperature, humidity, cloudiness, wind_speed, city_name name FROM current_weather WHERE city_name = %s", (city,))
            data = cur.fetchone()
            if data:
                return {
                    'name': city,
                    'main': {
                        'temp': data[0],
                        'humidity': data[1],
                    },
                    'clouds': {
                        'all': data[2],
                    },
                    'wind': {
                        'speed': data[3],
                    }
                }
            else:
                return None

# Функция для получения прогноза погоды из базы данных PostgreSQL
def get_weather_forecast_from_db(city):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT date_time temp_min, temp_max, humidity, cloudiness, wind_speed, city_name FROM forecast WHERE city_name = %s", (city,))
            data = cur.fetchone()
            if data and data[0]:
                forecast_data = data[0]
                # Убедитесь, что данные являются строкой перед десериализацией
                if isinstance(forecast_data, str):
                    try:
                        return json.loads(forecast_data)
                    except json.JSONDecodeError as e:
                        st.error(f"Ошибка декодирования данных прогноза погоды: {e}")
                        return None
                else:
                    st.error(f"Ожидались данные в формате строки, получен тип {type(forecast_data)}")
                    return None
            else:
                return None


# Функция для отображения главной страницы
def main_page():
    st.title("Приложение прогноза погоды")
    st.sidebar.title("Сайдбар")
    st.sidebar.write("Введите название города:")
    city_input = st.sidebar.text_input("Название города", key="city", on_change=load_weather)

    # Добавляем кнопку для подтверждения ввода
    if st.sidebar.button("Показать погоду"):
        load_weather()

def load_weather():
    city_input = st.session_state.city
    if city_input:
        if check_internet_connection():
            weather_data = get_weather_data_from_api(city_input)
            weather_forecast = get_weather_forecast_from_api(city_input) if weather_data else None
        else:
            st.warning("Отсутствует подключение к интернету. Данные будут взяты из базы данных.")
            weather_data = get_weather_data_from_db(city_input)
            weather_forecast = get_weather_forecast_from_db(city_input)
        
        if weather_data and weather_forecast:
            st.session_state.weather_data = weather_data
            st.session_state.weather_forecast = weather_forecast
            st.rerun()
        else:
            st.error("Данные о погоде не найдены. Попробуйте еще раз.")

# Функция для отображения страницы погоды
def weather_page():
    st.title("Страница погоды")
    if st.button("Вернуться на главную"):
        if 'weather_data' in st.session_state:
            del st.session_state['weather_data']
        if 'weather_forecast' in st.session_state:
            del st.session_state['weather_forecast']
        st.rerun()
    weather_data = st.session_state.get('weather_data')
    weather_forecast = st.session_state.get('weather_forecast')
    if weather_data:
        display_weather(weather_data, weather_forecast)
    else:
        st.error("Данные о погоде отсутствуют. Пожалуйста, попробуйте еще раз.")

def display_weather(weather_data, weather_forecast):
    city_name = weather_data.get('name')
    st.write(f"Погода в городе {city_name}:", datetime.now().strftime('%H:%M:%S'))
    current_weather = weather_data.get('main')
    cloudiness = weather_data.get('clouds')
    wind = weather_data.get('wind')
    st.write("Текущая погода:")
    st.write(f"Температура: {current_weather.get('temp')}°C")
    st.write(f"Влажность: {current_weather.get('humidity')}")
    if cloudiness:
        st.write(f"Облачность: {cloudiness.get('all')}")
    else:
        st.warning("Данные об облачности отсутствуют.")
    if wind:
        st.write(f"Скорость ветра: {wind.get('speed')}")
    else:
        st.warning("Данные о ветре отсутствуют.")

    st.write("Прогноз погоды на 4 дня:")
    if weather_forecast:
        display_forecast(weather_forecast)
    else:
        st.error("Данные о прогнозе погоды отсутствуют.")

def display_forecast(weather_forecast):
    today = datetime.now().date()  # Получаем текущую дату
    forecast_list = weather_forecast.get('list')
    dates_set = set()
    for forecast in forecast_list:
        forecast_date = datetime.fromtimestamp(forecast.get('dt')).date()
        if forecast_date > today and forecast_date not in dates_set and len(dates_set) < 4:
            dates_set.add(forecast_date)
            temperature = forecast.get('main', {}).get('temp')
            humidity = forecast.get('main', {}).get('humidity')
            cloudiness = forecast.get('clouds', {}).get('all')
            wind_speed = forecast.get('wind', {}).get('speed')
            st.write(f"Дата: {forecast_date.strftime('%d %B %Y')}")
            st.write(f"Температура: {temperature}°C")
            st.write(f"Влажность: {humidity}")
            st.write(f"Облачность: {cloudiness}")
            st.write(f"Скорость ветра: {wind_speed}")
            st.write("---")

# Основной блок кода Streamlit
if 'weather_data' not in st.session_state:
    main_page()
else:
    weather_page()


