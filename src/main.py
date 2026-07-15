from yolo_uno import *
from pins import *
from lcd1602 import *
from dht20 import *



import asyncio

# class Semaphore:
#     def __init__(self, value=1):
#         if value < 0:
#             raise ValueError("ValueError")
#         self.value = value
#         self.waiting = [] # List of tokens

#     async def acquire(self):
#         if self.value > 0:
#             self.value -= 1
#             return True
        
       
#         curr_task = asyncio.current_task() if hasattr(asyncio, 'current_task') else None
#         self.waiting.append(curr_task)
        
#         # Create an event for waiting
#         ev = asyncio.Event()
#         async def wait_placeholder():
#             await ev.wait()
            
#         # Pending loop
#         while self.value <= 0:
#             await asleep_ms(10) # Wait until token is released
#             if curr_task not in self.waiting: 
#                 break
                
#         self.value -= 1
#         return True

#     def release(self):
#         self.value += 1
            
#         if self.waiting:
#             # Release a token
#             task = self.waiting.pop(0)
# =====================================================================

class SensorUpdate:
    def __init__(self):
        self.temperature = 0
        self.humidity = 0
    def update(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

# Create global variable to keep track of latest sensor update 
latest_update = SensorUpdate()
    
# Create event
lcd_event = asyncio.Event()
heater_event = asyncio.Event()
cooler_event = asyncio.Event()
humidifier_event = asyncio.Event()

led_D13 = Pins(D13_PIN)
rgb_led_D3 = RGBLed(D3_PIN, 4) # Heater
rgb_led_D5 = RGBLed(D5_PIN, 4) # Cooler
rgb_led_D7 = RGBLed(D7_PIN, 4) # Humidifier

lcd1602 = LCD1602()
dht20 = DHT20()

def show_all(rgb_led, color):
    for i in range(4):
        rgb_led.show(i, color)

async def task_LED_Blinky():
  while True:
    await asleep_ms(1000)
    led_D13.toggle()
    
async def read_sensor_task():
    global latest_update
    
    while True:
        temp = await dht20.atemperature()
        humi = await dht20.ahumidity()
        
        latest_update.update(temp, humi)
        
        print("Temperature: {:.1f} C | Humidity: {:.1f} %".format(temp, humi))
        
        lcd_event.set() 
        heater_event.set() 
        cooler_event.set() 
        humidifier_event.set() 
            
        await asyncio.sleep_ms(5000)
    
async def lcd_task():
    global latest_update 
    
    while True:
        await lcd_event.wait() 
        lcd_event.clear() 
        
        temp = latest_update.temperature 
        humi = latest_update.humidity
        
        # LCD display
        lcd1602.clear()
        lcd1602.show("TEMP: ", 0, 0)
        lcd1602.show("{:.1f}".format(temp), 0, 6)
        lcd1602.show("C", 0, 11)
        lcd1602.show("HUMI: ", 1, 0)
        lcd1602.show("{:.1f}".format(humi), 1, 6)
        lcd1602.show("%", 1, 11)
    
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
    
    while True:
        await cooler_event.wait() 
        cooler_event.clear() 
        
        temp = latest_update.temperature 
        
        if temp >= 28:
            show_all(rgb_led_D5, (0, 255, 0))
            await asyncio.sleep_ms(5000)
        else:
            show_all(rgb_led_D5, (0, 0, 0))
            
async def humidifier_task():
    global latest_update 
    
    while True:
        await humidifier_event.wait() 
        humidifier_event.clear() 

        humi = latest_update.humidity 
        
        if humi < 40:
            show_all(rgb_led_D7, (0, 255, 0))    # GREEN
            await asyncio.sleep_ms(5000)
            
            show_all(rgb_led_D7, (255, 255, 0))  # YELLOW
            await asyncio.sleep_ms(3000)
            
            show_all(rgb_led_D7, (255, 0, 0))    # RED
            await asyncio.sleep_ms(2000)
        else:
            show_all(rgb_led_D7, (0, 0, 0))

async def setup():

  print('App started')

  create_task(task_LED_Blinky())
  create_task(read_sensor_task())
  create_task(lcd_task())
  create_task(heater_task())
  create_task(cooler_task())
  create_task(humidifier_task())


async def main():
  await setup()
  while True:
    await asleep_ms(100)

run_loop(main())
