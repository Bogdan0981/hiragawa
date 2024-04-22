import requests
import psycopg2
from datetime import datetime
import zipfile
from io import BytesIO
import time  

# Параметры для подключения к базе данных PostgreSQL
db_config = {
    "database": "postgres",
    "user": "postgres",
    "password": "kb0904",
    "host": "localhost",
    "port": "5433"
}

# Параметры для запроса к API
API_KEY = "2624fd25b511ea7d85afbcb3f9439698"
BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
UNITS = "metric"

def get_city_data():
    try:
        # Загрузка данных о городах из базы данных GeoNames
        response = requests.get("http://download.geonames.org/export/dump/cities5000.zip")
        cities = []
        with response, zipfile.ZipFile(BytesIO(response.content)) as z:
            with z.open('cities5000.txt') as f:
                for line in f:
                    cities.append(line.decode('utf-8').split('\t')[1])
        return cities
    except Exception as e:
        print(f"Ошибка при загрузке данных о городах: {e}")
        return None

def get_forecast_data(city_name):
    try:
        response = requests.get(f"{BASE_URL}q={city_name}&units={UNITS}&appid={API_KEY}")
        data = response.json()
        forecasts = []
        for item in data['list']:
            dt_txt = item['dt_txt']
            if "12:00:00" in dt_txt:
                forecasts.append({
                    "city_name": city_name,
                    "date_time": dt_txt,
                    "temp_min": item['main']['temp_min'],
                    "temp_max": item['main']['temp_max'],
                    "humidity": item['main']['humidity'],
                    "cloudiness": item['clouds']['all'],
                    "wind_speed": item['wind']['speed']
                })
        return forecasts
    except Exception as e:
        print(f"Ошибка при получении данных с API для города {city_name}: {e}")
        return []

def save_forecast_to_db(forecasts):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        for forecast in forecasts:
            cursor.execute(
                """
                INSERT INTO forecast (city_name, date_time, temp_max, temp_min, humidity, cloudiness, wind_speed)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (forecast['city_name'], forecast['date_time'], forecast['temp_min'], forecast['temp_max'], forecast['humidity'], forecast['cloudiness'], forecast['wind_speed'])
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("Прогноз погоды успешно сохранен в базу данных.")
    except Exception as e:
        print(f"Ошибка при сохранении данных в базу данных: {e}")

def main():
    cities = get_city_data()
    if cities:
        while True:
            for city in cities:
                forecasts = get_forecast_data(city)
                if forecasts:
                    save_forecast_to_db(forecasts)
                else:
                    print(f"Не удалось получить данные прогноза погоды для города {city}.")
            
            time.sleep(600)  # Пауза в 10 минут
    else:
        print("Не удалось получить список городов. Проверьте подключение к интернету и доступность источника данных.")

if __name__ == "__main__":
    main()
