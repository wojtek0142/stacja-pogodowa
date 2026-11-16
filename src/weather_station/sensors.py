from sqlalchemy import select
from .database import Base, engine, get_db, SessionLocal
import time
from . import models
import seeed_dht
from grove.display.jhd1802 import JHD1802

Base.metadata.create_all(bind=engine)

sensor = seeed_dht.DHT("11", 12)
lcd = JHD1802()

def print_lcd(temp: int, humi: int, lcd):
    lcd.backlight(False)
    time.sleep(1)
    lcd.clear()
    lcd.backlight(True)
    lcd.setCursor(0, 0)
    lcd.write(f"Temperatura: {temp} °C")
    lcd.setCursor(1,0)
    lcd.write(f"Wilgotność: {humi} %")

def read_values(sensor):  
    humi, temp = sensor.read()
    return humi, temp

while True:
    try:
        humi,temp = read_values(sensor)
        with SessionLocal() as db:
            db.add(models.Measurement(temperature=temp, humidity=humi,))
            db.commit()
    except Exception as e:
        print("Nie udalo się odczytać pomiaru")
    time.sleep(5)