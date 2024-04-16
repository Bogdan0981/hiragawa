from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import json
from datetime import date
from datetime import datetime

app = FastAPI()

# Настройки подключения к базе данных
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "kb0904"
DATABASE_NAME = "database"
DATABASE_HOST = "localhost"
DATABASE_PORT = "5433"

# Функция для создания подключения к базе данных
async def get_db_connection():
    return await asyncpg.connect(user=DATABASE_USER, password=DATABASE_PASSWORD, database=DATABASE_NAME, host=DATABASE_HOST, port=DATABASE_PORT)

# Модели Pydantic для ответов
class WeatherToday(BaseModel):
    id: int
    temperature: float
    humidity: int
    clouds: int
    wind_speed: float
    record_time: datetime

class Forecast(BaseModel):
    id: int
    min_temperature: float
    max_temperature: float
    humidity: int
    clouds: int
    wind_speed: float
    forecast_date: date

@app.get("/weather/today", response_model=list[WeatherToday])
async def read_weather_today():
    conn = await get_db_connection()
    rows = await conn.fetch("SELECT * FROM weather ORDER BY record_time DESC LIMIT 1")
    await conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return [dict(row) for row in rows]

@app.get("/weather/forecast", response_model=list[Forecast])
async def read_weather_forecast():
    conn = await get_db_connection()
    rows = await conn.fetch("SELECT * FROM forecast ORDER BY forecast_date")
    await conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Forecast data not found")
    return [dict(row) for row in rows]

