import requests
import psycopg2
from datetime import datetime
import time  # Импорт модуля time для задания паузы

# Параметры для подключения к базе данных PostgreSQL
db_config = {
    "database": "postgres",
    "user": "postgres",
    "password": "kb0904",
    "host": "localhost",
    "port": "5433"
}

# Параметры для запроса к API
API_KEY = "3bb2293d59e5ef49a57f2428c39e460b"
BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
CITY_NAME = "Прага"
UNITS = "metric"

def get_forecast_data():
    try:
        response = requests.get(f"{BASE_URL}q={CITY_NAME}&units={UNITS}&appid={API_KEY}")
        data = response.json()
        forecasts = []
        # Проходимся по списку прогнозов и выбираем одно время каждого дня (например, полдень)
        for item in data['list']:
            dt_txt = item['dt_txt']
            if "12:00:00" in dt_txt:  # Выбираем данные за полдень
                forecasts.append({
                    "date_time": dt_txt,
                    "temp_min": item['main']['temp_min'],
                    "temp_max": item['main']['temp_max'],
                    "humidity": item['main']['humidity'],
                    "cloudiness": item['clouds']['all'],
                    "wind_speed": item['wind']['speed']
                })
        return forecasts
    except Exception as e:
        print(f"Ошибка при получении данных с API: {e}")
        return []

def save_forecast_to_db(forecasts):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        for forecast in forecasts:
            cursor.execute(
                """
                INSERT INTO forecast (date_time, temp_max, temp_min, humidity, cloudiness, wind_speed)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (forecast['date_time'], forecast['temp_min'], forecast['temp_max'], forecast['humidity'], forecast['cloudiness'], forecast['wind_speed'])
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("Прогноз погоды успешно сохранен в базу данных.")
    except Exception as e:
        print(f"Ошибка при сохранении данных в базу данных: {e}")

def main():
    while True:  # Бесконечный цикл для периодического запуска
        forecasts = get_forecast_data()
        if forecasts:
            save_forecast_to_db(forecasts)
        else:
            print("Не удалось получить данные прогноза погоды.")
        time.sleep(20)  # Пауза на 4 часа (14400 секунд)

if __name__ == "__main__":
    main()
