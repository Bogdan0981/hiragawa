import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from scipy.interpolate import make_interp_spline
import numpy as np


def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

def get_hourly_forecast(hourly_forecast):
    forecast_intervals = hourly_forecast[:8]
    return forecast_intervals

def get_weather_data_from_api(city):
    api_key = "2624fd25b511ea7d85afbcb3f9439698"
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    forecast_5_days_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    
    current_weather_data = requests.get(weather_url).json()
    forecast_5_days_data = requests.get(forecast_5_days_url).json()

    forecast_24_hours_data = get_hourly_forecast(forecast_5_days_data['list'])

    return current_weather_data, forecast_5_days_data, forecast_24_hours_data

def main_page():
    st.title("Приложение прогноза погоды")
    configure_sidebar()
    city_input = st.sidebar.text_input("Название города", key='city')
    
    if st.sidebar.button("Показать погоду"):
        handle_weather_display(city_input)

def configure_sidebar():
    st.sidebar.title("Сайдбар")
    st.sidebar.write("Введите название города:")

def handle_weather_display(city_input):
    if check_internet_connection():
        try_fetching_weather_data(city_input)
    else:
        st.warning("Отсутствует подключение к интернету. Данные будут взяты из базы данных.")
        fetch_weather_from_db(city_input)

def try_fetching_weather_data(city_input):
    weather_data, forecast_5_days_data, forecast_24_hours_data = get_weather_data_from_api(city_input)
    if weather_data and forecast_5_days_data and forecast_24_hours_data:

        st.session_state.weather_data = weather_data
        st.session_state.forecast_5_days_data = forecast_5_days_data
        st.session_state.forecast_24_hours_data = forecast_24_hours_data
        weather_page()
    else:
        st.error("Не удалось получить данные о погоде. Попробуйте еще раз или проверьте название города.")

def fetch_weather_from_db(city_input):
    weather_data, forecast_5_days, forecast_24_hours = get_weather_data_from_api(city_input)
    if weather_data:
        update_weather_session(weather_data)
    else:
        st.error("Данные о погоде для данного города не найдены в базе данных.")

def update_weather_session(weather_data):
    st.session_state.weather_data = weather_data
    st.rerun()

def weather_page():
    st.title("Страница погоды")
    if 'weather_data' in st.session_state:
        city_name = st.session_state.weather_data['name']
        st.write(f"Погода в городе {city_name}:", datetime.now().strftime('%H:%M:%S'))
    else:
        st.error("Ошибка: данные о текущей погоде отсутствуют в сессии.")
    
    if 'forecast_5_days_data' in st.session_state:
        display_5_day_forecast(st.session_state.forecast_5_days_data)
    else:
        st.error("Ошибка: данные прогноза на 5 дней отсутствуют в сессии.")

    if 'forecast_24_hours_data' in st.session_state:
        display_24_hour_forecast(st.session_state.forecast_24_hours_data)
    else:
        st.error("Ошибка: данные прогноза на 24 часа отсутствуют в сессии.")

def display_5_day_forecast(forecast_5_days_data):
    st.header("Прогноз на 5 дней")
    forecast_df = pd.DataFrame([{
        'date': item['dt_txt'],
        'temp_min': item['main']['temp_min'],
        'temp_max': item['main']['temp_max'],
        'wind_speed': item['wind']['speed'],
        'weather': item['weather'][0]['main']
    } for item in forecast_5_days_data['list']])
    
    forecast_df['date'] = pd.to_datetime(forecast_df['date'])

    forecast_df = forecast_df.resample('D', on='date').agg({
        'temp_min': 'min',
        'temp_max': 'max',
        'wind_speed': 'mean',
        'weather': lambda x: x.mode()[0]
    })
    
    for index, row in forecast_df.iterrows():
        day = index.strftime('%A')
        temp_min = row['temp_min']
        temp_max = row['temp_max']
        wind_speed = row['wind_speed']
        weather = row['weather']
        
        st.write(f"{day}: {weather}, {temp_min}°C - {temp_max}°C, Средняя скорость ветра: {wind_speed:.1f} км/ч")


def display_24_hour_forecast(forecast_24_hours_data):
    st.subheader("Прогноз погоды на 24 часа")
    
    times = []
    temperatures = []
    wind_speeds = []
    
    for forecast in forecast_24_hours_data:
        forecast_time = datetime.fromtimestamp(forecast['dt']).strftime('%H:%M')
        times.append(forecast_time)
        
        temperature = forecast['main']['temp']
        temperatures.append(temperature)
        
        wind_speed = forecast['wind']['speed']
        wind_speeds.append(wind_speed)
        
        st.write(f"{forecast_time}: Температура {temperature}°C, Скорость ветра {wind_speed} м/с")
    

    trace_temp = go.Scatter(
        x=times, 
        y=temperatures, 
        mode='lines+text',
        text=[f"{t}°C" for t in temperatures],
        textposition="top center",
        line=dict(width=3, shape='spline', smoothing=1, color='#90a955'),
        textfont=dict(size=16)
    )
    

    annotations = [
        dict(
            x=times[i], 
            y=min(temperatures) - 1,
            text=f"{ws} м/с", 
            showarrow=False,
            xanchor='center',
            yanchor='top',
            font=dict(color='blue', size=16)
        ) for i, ws in enumerate(wind_speeds)
    ]
    
    layout = go.Layout(
        title='Изменение температуры по времени',
        xaxis=dict(
            tickfont=dict(size=15)
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=False,
        annotations=annotations
    )
    
    fig = go.Figure(data=[trace_temp], layout=layout)
    st.plotly_chart(fig, use_container_width=True)


if 'weather_data' not in st.session_state:
    main_page()
else:
    weather_page()