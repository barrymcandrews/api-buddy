#!/usr/bin/env bash

# Main Server
sudo python3 main.py &

# Sources
sudo python3 ./sources/spotify.py &
sudo python3 ./sources/weather.py &
sudo python3 ./sources/stocks.py &
sudo python3 ./sources/news.py &


