import requests
import psycopg2
from datetime import datetime
import time  # Импортируем модуль time

# Параметры для подключения к базе данных PostgreSQL
db_config = {
    "database": "postgres",
    "user": "postgres",
    "password": "kb0904",
    "host": "localhost",
    "port": "5433"
}

# Параметры для запроса к API
API_KEY = "ef4cfe7b51b74456e886d541c4c6bed4"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
CITY_NAME = "Прага"
UNITS = "metric"

def get_weather_data():
    try:
        response = requests.get(f"{BASE_URL}q={CITY_NAME}&units={UNITS}&appid={API_KEY}")
        data = response.json()
        return {
            "temperature": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "cloudiness": data['clouds']['all'],
            "wind_speed": data['wind']['speed']
        }
    except Exception as e:
        print(f"Ошибка при получении данных с API: {e}")
        return None

def save_data_to_db(weather_data):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            """
            INSERT INTO current_weather (record_time, temperature, humidity, cloudiness, wind_speed)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (now, weather_data['temperature'], weather_data['humidity'], weather_data['cloudiness'], weather_data['wind_speed'])
        )

        conn.commit()
        cursor.close()
        conn.close()
        print("Данные успешно сохранены в базу данных.")
    except Exception as e:
        print(f"Ошибка при сохранении данных в базу данных: {e}")

def main():
    while True:  # Бесконечный цикл
        weather_data = get_weather_data()
        if weather_data:
            save_data_to_db(weather_data)
        else:
            print("Не удалось получить данные о погоде.")
        
        time.sleep(20)  # Пауза в 10 минут

if __name__ == "__main__":
    main()
