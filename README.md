# Smart Climate Controller Using RTOS

An RTOS-style smart climate controller developed for the YoloUNO / ESP32-S3 platform.

This project can run on Yolo.

The project reads temperature and humidity from a DHT20 sensor, displays the newest values on an LCD1602, and uses RGB LEDs to simulate a heater, cooler, and humidifier. Independent asynchronous tasks handle periodic sensing, status blinking, display updates, and climate-control behavior.

## Run Online

This project runs on OhStem’s online simulation platform:

[Open the shared OhStem simulation](https://app.ohstem.vn/#!/share/vrb-project/3087fc76-33b8-46e5-9682-c07dbd68c176)

## Features

- Reads temperature and humidity from the DHT20 every 5 seconds
- Prints sensor readings to the Serial Monitor
- Updates an LCD1602 display with the latest values
- Blinks onboard LED D13 every 1 second as a system-status indicator
- Heater RGB LED on D3:
  - Green: temperature >= 18 C
  - Orange: 10 C < temperature < 18 C
  - Red: temperature <= 10 C
- Cooler RGB LED on D5:
  - Activates green for 5 seconds when temperature >= 28 C
- Humidifier RGB LED on D7:
  - Activates when humidity < 40%
  - Green for 5 seconds, yellow for 3 seconds, then red for 2 seconds

## Task Communication

The sensor task stores the latest temperature and humidity in a shared data object. It then signals separate Event-based binary notifications for the LCD, heater, cooler, and humidifier tasks.

This latest-value approach is used instead of a queue because the control tasks should respond to the most recent environmental state rather than process old sensor readings.

## Main Tasks

- `task_LED_Blinky()` — toggles LED D13 every second
- `read_sensor_task()` — reads DHT20 data every 5 seconds
- `lcd_task()` — updates LCD1602 after a sensor update
- `heater_task()` — selects the heater LED color
- `cooler_task()` — controls the 5-second cooling indication
- `humidifier_task()` — controls the timed humidifier LED sequence
