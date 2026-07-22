from yolo_uno import *
from pins import *
from lcd1602 import *
from dht20 import *
from abutton import *

import asyncio

# For updating latest sensor reading
class SensorUpdate:
    def __init__(self):
        self.temperature = 0
        self.humidity = 0
    def update(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

# For logging sensor readings
class DataLogger:
    def __init__(self):
        self.sample_count = 0

        # Create CSV header once
        with open("sensor_log.csv", "w") as f:
            f.write("Sample,Temperature,Humidity\n")

    def update_sensor(self, temp, humi):
        self.sample_count += 1

        # Append new record to file
        with open("sensor_log.csv", "a") as f:
            f.write("{},{},{}\n".format(
                self.sample_count,
                temp,
                humi
            ))
    
    def show_statistics(self):
        temps = []
        humis = []

        try:
            with open("sensor_log.csv", "r") as f:
                lines = f.readlines()

            print("===== CSV CONTENT =====")
            for line in lines:
                print(line.strip())
            print("=======================")

            for line in lines[1:]:   # Skip header
                sample, temp, humi = line.strip().split(",")

                temps.append(float(temp))
                humis.append(float(humi))

            if len(temps) == 0:
                print("No data available")
                return

            print("===== STATISTICS =====")
            print("Min Temp:", min(temps))
            print("Max Temp:", max(temps))
            print("Avg Temp:", sum(temps) / len(temps))

            print("Min Humi:", min(humis))
            print("Max Humi:", max(humis))
            print("Avg Humi:", sum(humis) / len(humis))

            print("======================")

        except Exception as e:
            print("Error reading statistics:", e)

# Create global variable to keep track of latest sensor update 
latest_update = SensorUpdate()

# Create a variable for data logging
data_logger = DataLogger()

# Configurable thresholds
cooler_threshold = 28
humidity_threshold = 40

# create 2 buttons to configurate thresholds
btn_A = aButton(D9_PIN)
btn_B = aButton(D10_PIN)

# Button for showing statistics
btn_BOOT = aButton(BOOT_PIN)

    
# Create event
lcd_event = asyncio.Event()
heater_event = asyncio.Event()
cooler_event = asyncio.Event()
humidifier_event = asyncio.Event()

led_D13 = Pins(D13_PIN)
rgb_led_D3 = RGBLed(D3_PIN, 4)
rgb_led_D5 = RGBLed(D5_PIN, 4)
rgb_led_D7 = RGBLed(D7_PIN, 4)

lcd1602 = LCD1602()
dht20 = DHT20()

# Helper function to show LEDs
def show_all(rgb_led, color):
    for i in range(4):
        rgb_led.show(i, color)

async def task_LED_Blinky():
  while True:
    await asleep_ms(1000)
    led_D13.toggle()
    
async def read_sensor_task():
    global latest_update
    global data_logger
    
    while True:
        temp = await dht20.atemperature()
        humi = await dht20.ahumidity()
        
        latest_update.update(temp, humi)
        data_logger.update_sensor(temp, humi)
        
        print("[{} ms] Temperature: {:.1f} C | Humidity: {:.1f} %".format(time.ticks_ms(), temp, humi))    
            
        lcd_event.set() 
        heater_event.set() 
        cooler_event.set() 
        humidifier_event.set() 
            
        await asyncio.sleep_ms(5000)
    
async def lcd_task():
    global latest_update 
    global cooler_threshold
    global humidity_threshold
    
    while True:
        await lcd_event.wait() 
        lcd_event.clear() 
        
        temp = latest_update.temperature 
        humi = latest_update.humidity
        
        # LCD display temperature and humidity
        lcd1602.clear()
        lcd1602.show("TEMP: ", 0, 0)
        lcd1602.show(str(int(temp)), 0, 5)
        lcd1602.show("C", 0, 8)
        lcd1602.show("HUMI: ", 1, 0)
        lcd1602.show(str(int(humi)), 1, 5)
        lcd1602.show("%", 1, 8)

        #LCD display thresholds
        lcd1602.show("CT:{}".format(cooler_threshold), 0, 10)
        lcd1602.show("HT:{}".format(humidity_threshold), 1, 10)
    
async def heater_task():
    global latest_update 
    
    while True:
        await heater_event.wait() 
        heater_event.clear() 
        
        temp = latest_update.temperature

        if temp >= 18:
            show_all(rgb_led_D3, (0, 255, 0))    # GREEN
        elif temp > 10:
            show_all(rgb_led_D3, (255, 165, 0))  # ORANGE
        else:
            show_all(rgb_led_D3, (255, 0, 0))    # RED 

async def cooler_task():
    global latest_update 
    global cooler_threshold
    
    while True:
        await cooler_event.wait() 
        cooler_event.clear() 
    
        temp = latest_update.temperature 
        
        if temp >= cooler_threshold:
            show_all(rgb_led_D5, (0, 255, 0))   # GREEN/ON
            await asyncio.sleep_ms(5000)

            show_all(rgb_led_D5, (0, 0, 0))     # OFF
        else:
            show_all(rgb_led_D5, (0, 0, 0))     # OFF
            
async def humidifier_task():
    global latest_update 
    global humidity_threshold
    
    while True:
        await humidifier_event.wait() 
        humidifier_event.clear() 

        humi = latest_update.humidity 
        
        if humi < humidity_threshold:
            show_all(rgb_led_D7, (0, 255, 0))    # GREEN
            await asyncio.sleep_ms(5000)
            
            show_all(rgb_led_D7, (255, 255, 0))  # YELLOW
            await asyncio.sleep_ms(3000)
            
            show_all(rgb_led_D7, (255, 0, 0))    # RED
            await asyncio.sleep_ms(2000)

            show_all(rgb_led_D7, (0, 0, 0))     # OFF
        else:
            show_all(rgb_led_D7, (0, 0, 0))     # OFF

# Showing statistics
async def on_boot_pressed():
    global data_logger
    data_logger.show_statistics()

async def on_btn_A_pressed():
    global cooler_threshold

    cooler_threshold += 1
    print("Cooler threshold:", cooler_threshold)

async def on_btn_A_long_pressed():
    global humidity_threshold

    humidity_threshold += 1
    print("Humidity threshold:", humidity_threshold)

async def on_btn_B_pressed():
    global cooler_threshold

    cooler_threshold -= 1
    print("Cooler threshold:", cooler_threshold)

async def on_btn_B_long_pressed():
    global humidity_threshold

    humidity_threshold -= 1
    print("Humidity threshold:", humidity_threshold)

async def setup():
    
    print('App started')

    create_task(task_LED_Blinky())
    create_task(read_sensor_task())
    create_task(lcd_task())
    create_task(heater_task())
    create_task(cooler_task())
    create_task(humidifier_task())

    # Button for showing statistics
    btn_BOOT.pressed(on_boot_pressed)

    # Buttons for configuring thresholds
    btn_A.pressed(on_btn_A_pressed)
    btn_A.long_pressed(on_btn_A_long_pressed)
    btn_B.pressed(on_btn_B_pressed)
    btn_B.long_pressed(on_btn_B_long_pressed)


async def main():
    await setup()
    while True:
        await asleep_ms(100)

run_loop(main())
