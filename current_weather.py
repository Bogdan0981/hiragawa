import requests
import psycopg2
from datetime import datetime
import time  
from io import BytesIO
import zipfile
import csv  

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
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
UNITS = "metric"

def get_city_data():
    try:
        # Загрузка данных о городах из базы данных GeoNames
        response = requests.get("http://download.geonames.org/export/dump/cities5000.zip")
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            with z.open('cities5000.txt') as f:
                cities = [line.decode('utf-8').split('\t')[1] for line in f]
        return cities
    except Exception as e:
        print(f"Ошибка при загрузке данных о городах: {e}")
        return None

def get_weather_data(city_name):
    try:
        response = requests.get(f"{BASE_URL}q={city_name}&units={UNITS}&appid={API_KEY}")
        data = response.json()
        return {
            "city_name": city_name,
            "temperature": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "cloudiness": data['clouds']['all'],
            "wind_speed": data['wind']['speed']
        }
    except Exception as e:
        print(f"Ошибка при получении данных с API для города {city_name}: {e}")
        return None

def save_data_to_db(weather_data):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            """
            INSERT INTO current_weather (record_time, city_name, temperature, humidity, cloudiness, wind_speed)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (now, weather_data['city_name'], weather_data['temperature'], weather_data['humidity'], weather_data['cloudiness'], weather_data['wind_speed'])
        )

        conn.commit()
        cursor.close()
        conn.close()
        print(f"Данные для города {weather_data['city_name']} успешно сохранены в базу данных.")
    except Exception as e:
        print(f"Ошибка при сохранении данных в базу данных для города {weather_data['city_name']}: {e}")

def main():
    cities = get_city_data()  # Получаем список городов
    if cities:
        while True:  
            for city in cities:
                weather_data = get_weather_data(city)
                if weather_data:
                    save_data_to_db(weather_data)
                else:
                    print(f"Не удалось получить данные о погоде для города {city}.")
            
            time.sleep(1000)  # Пауза в 10 минут
    else:
        print("Не удалось получить список городов. Проверьте подключение к интернету и доступность источника данных.")

if __name__ == "__main__":
    main()
