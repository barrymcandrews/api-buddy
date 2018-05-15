# LED Matrix Controller

This project lets you control a [LED Matrix](https://www.adafruit.com/product/420) with a web-connected Raspberry Pi. 

##### Controlled by MQTT

You can control the content of the matrix by connecting 
it to the MQTT server of your choice. This makes it easy to integrate with other IoT appliances.

##### Information at a Glance

This project downloads information in the background from REST APIs, so it's displaying up-to-date information before you know you need it. The home screen is also completely customizable.


## Getting Started

For information on how to set up the hardware see [this guide](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/driving-matrices)

### Prerequisites

 * Python 3.6 
 * [Hzeller Library](https://github.com/hzeller/rpi-rgb-led-matrix)
 * Pillow

### Running the Program

If this is your first time running the program make sure you run `setup.py` first. This will ensure all python dependencies are met.

Once `setup.py` is complete just run `./led_matrix/main.py`

```bash
$ sudo chmod +x led_matrix/main.py
$ ./led_matrix/main.py
```

#### Content Sources
The project currently has two content sources:

 * News - News Api
 * Weather - OpenWeatherMap
 
Other sources are planned to be implemented in the future:
 
 * Spotify
 * Stocks

#### About
This project was written for Steelhacks 2018

