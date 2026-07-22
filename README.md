# Smart Controller System using RTOS

An event-driven, RTOS-based climate control simulation built for the YoloUNO (ESP32-S3) microcontroller. 

This project uses asynchronous tasks (`asyncio`) to read temperature and humidity from a DHT20 sensor, display values on an LCD1602, and simulate a heater, cooler, and humidifier using RGB LEDs.

## Run Online

This project runs on OhStem’s online simulation platform:

[Open the shared OhStem simulation](https://app.ohstem.vn/#!/share/vrb-project/3087fc76-33b8-46e5-9682-c07dbd68c176)

## Features

- **Real-Time Sensing:** Reads temperature and humidity from the DHT20 every 5 seconds and prints to the Serial Monitor.
- **Display:** Updates an LCD1602 display with the latest sensor values and configured threshold settings.
- **System Indicator:** Blinks the onboard LED D13 every 1 second to confirm the event loop is running.
- **Heater Simulation (RGB LED D3):**
  - **Green:** Temperature >= 18°C (Safe)
  - **Orange:** 10°C < Temperature < 18°C (Warning)
  - **Red:** Temperature <= 10°C (Critical)
- **Cooler Simulation (RGB LED D5):**
  - Activates **Green** for 5 seconds when temperature >= 28°C.
- **Humidifier Simulation (RGB LED D7):**
  - Activates when humidity < 40%.
  - Sequence: **Green** (5s) -> **Yellow** (3s) -> **Red** (2s).

## Advanced Features

- **Data Logging:** Periodically saves all sensor readings to `sensor_log.csv` stored in the YoloUNO flash memory.
- **System Statistics:** Pressing the **BOOT** button calculates and prints the min, max, and average temperature and humidity values to the Serial Monitor.
- **Adjustable Thresholds:** 
  - **Button A/B (Short Press):** Increase/decrease the cooler temperature threshold.
  - **Button A/B (Long Press):** Increase/decrease the humidifier humidity threshold.

## Task Communication

The sensor task acts as the data producer. It reads the sensor data, stores it in a shared `latest_update` object, and uses four binary `asyncio.Event` flags to signal the consumer tasks (LCD, heater, cooler, humidifier).

This latest-value approach is chosen over a queue to ensure control tasks respond only to the most current environmental state, preventing delayed reactions from outdated measurements.

## Main Tasks

- `task_LED_Blinky()` — Toggles onboard LED every second
- `read_sensor_task()` — Reads DHT20 data every 5 seconds, logs it, and triggers events
- `lcd_task()` — Updates the LCD1602 after an event trigger
- `heater_task()` — Selects the heater LED color based on current temperature
- `cooler_task()` — Runs the 5-second cooling indicator if needed
- `humidifier_task()` — Runs the timed humidifier sequence if needed
