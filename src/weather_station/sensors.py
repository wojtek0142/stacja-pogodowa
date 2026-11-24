from .database import Base, engine, get_db, SessionLocal
import time
from . import models
import seeed_dht
from grove.display.jhd1802 import JHD1802
from grove.factory import Factory

Base.metadata.create_all(bind=engine)

sensor = seeed_dht.DHT("11", 12)
lcd = JHD1802()
led = Factory.getOneLed("GPIO-HIGH", 5)
led.light(False)

def print_lcd(temp: float, humi: float, lcd):
    lcd.clear()
    lcd.backlight(True)
    lcd.home()
    lcd.write(f"Temp: {temp} C")
    lcd.setCursor(1,0)
    lcd.write(f"Wilgotnosc: {humi} %")

def read_values(sensor):  
    humi, temp = sensor.read()
    return humi, temp

while True:
    try:
        humi,temp = read_values(sensor)
        if temp >= 30:
            led.light(True)
        else:
            led.light(False)
        print_lcd(temp,humi,lcd)
        with SessionLocal() as db:
            db.add(models.Measurement(temperature=temp, humidity=humi,))
            db.commit()
    except Exception as e:
        print("Nie udalo się odczytać pomiaru")
    time.sleep(60)