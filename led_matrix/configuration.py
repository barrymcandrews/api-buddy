import configparser
import rgbmatrix

parser = configparser.ConfigParser()
parser.read('defaults.conf')

# Section Titles
MATRIX = 'matrix'
MQTT = 'mqtt'
HOME = 'home'

# Matrix Settings
matrix_options = rgbmatrix.RGBMatrixOptions()
matrix_options.brightness = parser[MATRIX].getint('brightness')
matrix_options.rows = parser[MATRIX].getint('rows')
matrix_options.cols = parser[MATRIX].getint('cols')
matrix_options.chain_length = parser[MATRIX].getint('chain_length')
matrix_options.parallel = parser[MATRIX].getint('parallel')
matrix_options.hardware_mapping = parser[MATRIX].get('hardware_mapping')
matrix_options.scan_mode = 1


# MQTT Settings
class MqttOptions(object):
    broker_url: str = parser[MQTT].get('broker_url')
    ca_file: str = parser[MQTT].get('ca_file')
    client_cert_file: str = parser[MQTT].get('client_cert_file')
    client_key_file: str = parser[MQTT].get('client_key_file')
    topic_prefix: str = parser[MQTT].get('topic_prefix')


# Home Settings
class HomeOptions(object):
    enabled: bool = parser[HOME].getboolean('enabled', fallback=False)
    show_time: bool = parser[HOME].getboolean('show_time', fallback=False)
    show_weather: bool = parser[HOME].getboolean('show_weather', fallback=False)
    show_news: bool = parser[HOME].getboolean('show_news', fallback=False)
    show_spotify: bool = parser[HOME].getboolean('show_spotify', fallback=False)
    show_stocks: bool = parser[HOME].getboolean('show_spotify', fallback=False)

