from setproctitle import setproctitle

import requests
import time
# api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=5d828247d61c0e4d3bb35dc1e30f3fde&q=Boston'
# json_data = requests.get(api_address).json()
# #print(json_data)
# formatted_data= json_data['main']['temp']
# #tree= ElementTree.fromstring(xml_data.content)
# #print(formatted_data)

# Taking the json data and creating a xml file format
# Writing the temp of city to text file


def create_xml():
    api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=5d828247d61c0e4d3bb35dc1e30f3fde&q=Pittsburgh'
    json_data = requests.get(api_address).json()
    message = '<message type="scroll" color="#0000FF" style="bold"> Weather in ' + json_data['name'] + ":    "
    deg_f = str(round(((json_data['main']['temp'] - 273.15) * 1.8) + 32))
    message += deg_f + "°F        "
    message += json_data['weather'][0]['description']
    message += "</message>"
    print(message)

    file = open("/tmp/led-source-weather", "w")
    file.write(message)
    file.flush()
    file.close()
    time.sleep(120)


if __name__ == "__main__":
    setproctitle("msource-weather")
    while True:
        create_xml()

