
from fastapi import Depends, FastAPI, Query, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import random
from pathlib import Path
from .schemas import ReadingBase
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from . import models
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
    result = db.execute(
            select(models.Measurement).order_by(models.Measurement.measured_at.desc()).limit(1)
        )
    latest = result.scalars().first()
    dew_point = None
    if latest:
        c = 243.04
        b = 17.625
        gamma = log(latest.humidity/100) + (b * latest.temperature / ( c + latest.temperature))
        dew_point = c * gamma / (b - gamma)
        dew_point = round(dew_point, 1)
    return templates.TemplateResponse(request, "index.html", {"measurements": latest, "dew_point":dew_point})


@app.get("/api/readings", response_model=ReadingBase)
def get_reading(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Measurement).order_by(models.Measurement.measured_at.asc())
    )
    latest = result.scalars().first()
    if latest:
        return latest

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No readings")


# def background_task(sensor, lcd):
#     while True:
#         humi, temp = read_values(sensor)
#         print_lcd(temp, humi, lcd)
#         time.sleep(10)

def sensor_test():
    humi = random.randint(38,59)
    temp = random.randint(15,30)
    return humi, temp