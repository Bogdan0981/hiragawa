import streamlit as st
import psycopg2
import requests
from datetime import datetime, timedelta

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
    api_key = "2624fd25b511ea7d85afbcb3f9439698"  # Замените на свой API ключ OpenWeather
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Функция для получения прогноза погоды на 5 дней из API OpenWeather
def get_weather_forecast_from_api(city):
    api_key = "2624fd25b511ea7d85afbcb3f9439698"  # Замените на свой API ключ OpenWeather
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
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
                st.session_state.weather_forecast = get_weather_forecast_from_api(city_input)
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
    weather_data = st.session_state.get('weather_data')
    weather_forecast = st.session_state.get('weather_forecast')
    if weather_data:
        city_name = weather_data.get('name')
        st.write(f"Погода в городе {city_name}:", datetime.now().strftime('%H:%M:%S'))
        current_weather = weather_data.get('main')
        cloudiness = weather_data.get('clouds')
        wind = weather_data.get('wind')
        st.write("Текущая погода:")
        st.write(f"Температура: {current_weather.get('temp')}°C")
        st.write(f"Влажность: {current_weather.get('humidity')}")
        if cloudiness is not None:
            st.write(f"Облачность: {cloudiness.get('all')}")
        else:
            st.warning("Данные об облачности отсутствуют.")
        st.write(f"Скорость ветра: {wind.get('speed')}")
        
        # Отображение прогноза погоды на 4 дня
        st.write("Прогноз погоды на 4 дня:")
        if weather_forecast:
            forecast_list = weather_forecast.get('list', [])
            dates_set = set()
            for forecast in forecast_list:
                forecast_date = datetime.fromtimestamp(forecast.get('dt')).date()
                if forecast_date not in dates_set and len(dates_set) < 4:
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
        else:
            st.error("Данные о прогнозе погоды отсутствуют.")
    else:
        st.error("Данные о погоде отсутствуют. Пожалуйста, попробуйте еще раз или подключитесь к интернету.")

    # Кнопка "Вернуться на главную"
    if st.button("Вернуться на главную"):
        st.session_state.weather_data = None
        st.session_state.weather_forecast = None
        main_page()


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
