
from fastapi import Depends, FastAPI, Query, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone,timedelta, UTC
import random
from pathlib import Path
from .schemas import ReadingBase
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Measurement 
from .database import Base, engine, get_db
from math import log


Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory= Path(__file__).parent / "templates")
app.mount("/static", StaticFiles(directory= Path(__file__).parent / "static"), name="static")

measurements: list[dict] = [
    {"id": 1, "temperature": 21.5, "humidity": 45.0, "measured_at": datetime(2026, 11, 12, 8, 0)},
    {"id": 2,"temperature": 22.1, "humidity": 43.2, "measured_at": datetime(2026, 11, 12, 9, 0)},
    {"id": 3,"temperature": 23.8, "humidity": 41.7, "measured_at": datetime(2026, 11, 12, 10, 0)},
    {"id": 4,"temperature": 24.3, "humidity": 40.5, "measured_at": datetime(2026, 11, 12, 11, 0)},
    {"id": 5,"temperature": 22.9, "humidity": 44.8, "measured_at": datetime(2026, 11, 12, 12, 0)},
]


@app.get("/", include_in_schema=False)
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result_last = db.execute(
            select(Measurement).order_by(Measurement.measured_at.desc()).limit(1)
        )
    latest = result_last.scalars().first()
    dew_point = None
    measured_time = None
    since = datetime.now(UTC) - timedelta(days=1)
    result_24H = db.execute(
            select(Measurement).where(Measurement.measured_at >= since)
            .order_by(Measurement.measured_at.asc())
        )
    temperature_stats: dict = {}
    temperatures = []
    humidity_stats: dict = {}
    humidities = []
    results_24H = result_24H.scalars().all()
    for measurement in results_24H:
        temperatures.append(measurement.temperature)
        humidities.append(measurement.humidity)
    temperature_stats["avg"] = sum(temperatures)/len(temperatures)
    temperature_stats["min"] = min(temperatures)
    temperature_stats["max"] = max(temperatures)
    humidity_stats["avg"] = sum(humidities)/len(humidities)
    humidity_stats["min"] = min(humidities)
    humidity_stats["max"] = max(humidities)
    if latest:
        dew_point = calc_dew_point(latest)
        if latest.measured_at.tzinfo is None:
            latest.measured_at = latest.measured_at.replace(tzinfo=UTC)
        measured_time = int(latest.measured_at.timestamp() * 1000)
    
    return templates.TemplateResponse(request, "index.html", {"measurements": latest, "dew_point":dew_point, "measured_at": measured_time, "temperature_stats": temperature_stats, "humidity_stats": humidity_stats})


@app.get("/api/measurements/", response_model=list[ReadingBase])
def get_readings(days: int,db: Annotated[Session, Depends(get_db)]):
    since = datetime.now(UTC) - timedelta(days=days)
    result = db.execute(
        select(Measurement).where(Measurement.measured_at >= since)
        .order_by(Measurement.measured_at.asc())
    )
    return result.scalars().all()


def calc_dew_point(latest: Measurement) -> float:
    c = 243.04
    b = 17.625
    gamma = log(latest.humidity/100) + (b * latest.temperature / ( c + latest.temperature))
    dew_point = c * gamma / (b - gamma)
    dew_point = round(dew_point, 1)
    return dew_point
