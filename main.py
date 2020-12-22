# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 20:49:31 2020

@author: icalderon

For a weather station over a raspberry pi4 board. Using BME280 for temperature,
humidity and pressure acquisition and adafruit anemometer with analog voltage output plus
an ADS1015 analog to digital converter for reading the wind speed.

Built from these examples: 
https://pypi.org/project/adafruit-circuitpython-bme280/
https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15

"""


import mysql.connect as mariadb
import board
#import digitalio
import busio
import adafruit_bme280
import time
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

def wind_meas(add):
    ads = ADS.ADS1015(add)
    chan = AnalogIn(ads, ADS.P0)
    return (19.636*chan.voltage-6.8727)

def bme280_meas(add):
    #i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(add)
    return bme280.temperature, bme280.humidity, bme280.pressure

def main_measurement():
    # pass
    conn = mariadb.connect(
        user="user_name",
        password="password",
        host="localhost",
        database="WEATHER")
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS meteoDB (n INT(22) NOT NULL AUTO_INCREMENT, Hora TIMESTAMP, Temp FLOAT, Hum FLOAT, Press FLOAT, Wind FLOAT, PRIMARY KEY (n))')
    
    temperature, humidity, pressure = bme280_meas(i2c)
    # humidity = bme280.humidity
    # pressure = bme280.pressure
    wind = wind_meas(i2c)
    
    try:
        cur.execute("INSERT INTO meteoDB (Temp, Hum, Press, Wind) VALUES (%s,%s,%s,%s)",(temperature, humidity,pressure/980.665,wind))
        print(time.strftime('%m-%d-%H:%M') + " {0:0.1f}*C,{1:0.1f}%,{2:0.1f}atm,{3:0.1f}[m/s]".format(temperature, humidity,pressure/980.665,wind))
    except mariadb.Error as e:
        print("Error: " + e)
    conn.commit()
    print(f'last Inserted ID: {cur.lastrowid}')

if __name__ == "__main__":
    while True:
        main_measurement()
        time.sleep(60)