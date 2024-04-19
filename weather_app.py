import streamlit as st
import psycopg2
import requests

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

# Функция для сохранения данных о погоде в базу данных PostgreSQL
def save_weather_data_to_db(weather_data):
    try:
        cur.execute("""
            INSERT INTO weather_data (record_time, temperature, humidity, cloudiness, wind_speed)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            weather_data['name'],
            weather_data['main']['record_time'],
            weather_data['main']['temperature'],
            weather_data['main']['humidity'],
            weather_data['main']['cloudiness'],
            weather_data['man']['wind_speed']
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Ошибка при сохранении данных в базу данных: {e}")

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
                st.experimental_rerun()
            else:
                st.error("Город не найден. Попробуйте еще раз или используйте сохраненные данные.")
        else:
            st.warning("Отсутствует подключение к интернету. Данные будут взяты из базы данных.")
            weather_data = get_weather_data_from_db(city_input)
            if weather_data:
                st.session_state.weather_data = weather_data
                st.experimental_rerun()
            else:
                st.error("Данные о погоде для данного города не найдены в базе данных.")

# Функция для отображения страницы погоды
def weather_page():
    st.title("Страница погоды")
    city_name = st.session_state.weather_data['name']
    st.write(f"Погода в городе {city_name}:")
    current_weather = st.session_state.weather_data['main']
    st.write("Текущая погода:")
    st.write(f"Температура: {current_weather['record_time']}°C")
    st.write(f"Ощущается как: {current_weather['feels_like']}°C")
    st.write(f"Минимальная температура: {current_weather['temp_min']}°C")
    st.write(f"Максимальная температура: {current_weather['temp_max']}°C")
    st.write(f"Влажность: {current_weather['humidity']}%")

# Функция для получения данных о погоде из базы данных PostgreSQL
def get_weather_data_from_db(city):
    cur.execute("SELECT * FROM current_weather", (city,))
    data = cur.fetchone()
    if data:
        return {
            'name': data[0],
            'main': {
                'temp': data[1],
                'feels_like': data[2],
                'temp_min': data[3],
                'temp_max': data[4],
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