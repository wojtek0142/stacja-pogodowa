
from collections.abc import Sequence
import csv
import io
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone,timedelta, UTC
from pathlib import Path
from .schemas import ReadingBase
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Measurement 
from .database import Base, engine, get_db
from math import log
import requests


Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory= Path(__file__).parent / "templates")
app.mount("/static", StaticFiles(directory= Path(__file__).parent / "static"), name="static")
URL = ""

@app.get("/", include_in_schema=False)
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result_last = db.execute(
            select(Measurement).order_by(Measurement.measured_at.desc()).limit(1)
        )
    latest = result_last.scalars().first()
    dew_point = None
    temp_trend = None
    humidity_trend = None
    measured_time = None
    since = datetime.now(UTC) - timedelta(days=1)
    result_24H = db.execute(
            select(Measurement).where(Measurement.measured_at >= since)
            .order_by(Measurement.measured_at.asc())
        )
    results_24H = result_24H.scalars().all()
    temperature_stats, humidity_stats = calc_statistics_24H(results_24H)
    start = datetime.now(UTC) - timedelta(minutes=65)
    end = datetime.now(UTC) - timedelta(minutes=60)
    hour_before = db.execute(
        select(Measurement).where(Measurement.measured_at >= start).where(Measurement.measured_at <= end)
    )
    hour_before_avg = hour_before.scalars().all()
    alert = False
    if latest:
        dew_point = calc_dew_point(latest)
        avg_temp, avg_hum = calc_avg(hour_before_avg)
        if latest.temperature >= 30:
             alert= True
        if avg_temp is not None and avg_hum is not None:
            temp_trend = latest.temperature - avg_temp
            humidity_trend = latest.humidity - avg_hum
        if latest.measured_at.tzinfo is None:
            latest.measured_at = latest.measured_at.replace(tzinfo=UTC)
        measured_time = int(latest.measured_at.timestamp() * 1000)
    
    return templates.TemplateResponse(request, "index.html", {"measurements": latest, "dew_point":dew_point, "measured_at": measured_time, "temperature_stats": temperature_stats, "humidity_stats": humidity_stats, "temp_trend":temp_trend, "humidity_trend": humidity_trend, "alert": alert})


@app.get("/api/measurements/", response_model=list[ReadingBase])
def get_readings(days: int,db: Annotated[Session, Depends(get_db)]):
    since = datetime.now(UTC) - timedelta(days=days)
    result = db.execute(
        select(Measurement).where(Measurement.measured_at >= since)
        .order_by(Measurement.measured_at.asc())
    )
    return result.scalars().all()

@app.get("/api/external/")
def services_data():
    url_meteo = "https://danepubliczne.imgw.pl/api/data/meteo/"
    url_open_meteo="https://api.open-meteo.com/v1/forecast?latitude=50.0614&longitude=19.9366&current=temperature_2m,relative_humidity_2m&timezone=Europe%2FBerlin"
    stacje_krakow = ["350190566","250190470","250190390","250190930"]
    try:
        response_meteo = requests.get(url_meteo, timeout=10)
        response = response_meteo.json()
        stations = [stacja for stacja in response if stacja["kod_stacji"] in stacje_krakow]
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Błąd IMGW: {e}")
    try:
        response_open_meteo = requests.get(url_open_meteo, timeout=10)
        response_2 = response_open_meteo.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Błąd Open-Meteo: {e}")
    send = {}
    for station in stations:
        name = station["nazwa_stacji"].split("-")[1]
        temperature = station["temperatura_powietrza"]
        humidity = station["wilgotnosc_wzgledna"]
        time = parse_date(station["temperatura_powietrza_data"])
        send[name] = {}
        send[name]["temperature"] = temperature
        send[name]["humidity"] = humidity
        send[name]["time"] = time
    send["Open-Meteo.com Krakow"] = {}
    send["Open-Meteo.com Krakow"]["time"] = parse_date(response_2["current"]["time"])
    send["Open-Meteo.com Krakow"]["humidity"] = response_2["current"]["relative_humidity_2m"]
    send["Open-Meteo.com Krakow"]["temperature"] = response_2["current"]["temperature_2m"]
    return send    
    

@app.get("/csv")
def download_csv(db: Session = Depends(get_db)):
    measurements = db.execute(select(Measurement)).scalars().all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["temperature", "humidity", "measured_at"])

    for measurement in measurements:
        writer.writerow([measurement.temperature, measurement.humidity, measurement.measured_at])
    csv_content = output.getvalue()
    return Response(
         content=csv_content,
         media_type ="text/csv",
         headers={
              "Content-Disposition": 'attachment; filename="readings.csv"'
         }
    )





def calc_dew_point(latest: Measurement) -> float:
    c = 243.04
    b = 17.625
    gamma = log(latest.humidity/100) + (b * latest.temperature / ( c + latest.temperature))
    dew_point = c * gamma / (b - gamma)
    dew_point = round(dew_point, 1)
    return dew_point

def calc_statistics_24H(results_24H: Sequence[Measurement]):
    if results_24H is None:
        return None, None
    temperature_stats: dict = {}
    temperatures = []
    humidity_stats: dict = {}
    humidities = []
    for measurement in results_24H:
        temperatures.append(measurement.temperature)
        humidities.append(measurement.humidity)
    temperature_stats["avg"] = round(sum(temperatures)/len(temperatures),2)
    temperature_stats["min"] = min(temperatures)
    temperature_stats["max"] = max(temperatures)
    humidity_stats["avg"] = round(sum(humidities)/len(humidities),2)
    humidity_stats["min"] = min(humidities)
    humidity_stats["max"] = max(humidities)
    return temperature_stats, humidity_stats

def calc_avg(hour_before_avg):
    if not hour_before_avg:
            return None, None
    temperatures = []
    humidities = []
    for measurement in hour_before_avg:
            temperatures.append(measurement.temperature)
            humidities.append(measurement.humidity)
    avg_temp = round(sum(temperatures)/len(temperatures),2)
    avg_hum = round(sum(humidities)/len(humidities),2)
    return avg_temp, avg_hum

def parse_date(timestamp):
    return datetime.fromisoformat(timestamp).strftime("%H:%M")