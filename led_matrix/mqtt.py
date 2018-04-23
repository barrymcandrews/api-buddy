import json

from hbmqtt.session import ApplicationMessage
from led_matrix import matrix, configuration
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1
from led_matrix.router import Router
from led_matrix.views import ScrollingTextView, AnimatedImageView

config = configuration.mqtt_options
client = MQTTClient(config={
    'certfile': config.client_cert_file,
    'keyfile': config.client_key_file
})
router = Router(client=client)


async def start_client():
    await client.connect(uri=config.broker_url, cafile=config.ca_file)
    print("Connected to MQTT Broker @ " + config.broker_url)

    await client.subscribe([(t.topic, t.qos) for t in router.topics])
    while True:
        try:
            await router.push(await client.deliver_message())
        except Exception as e:
            print(e)
            raise


@router.topic('aurora/+/+/matrix/view', QOS_1)
async def handle_view(message, wild1, wild2):
    view_settings = json.loads(message.data)


@router.topic('aurora/+/+/matrix/view/clear', QOS_1)
async def handle_view(message, wild1, wild2):
    matrix.user_view = None


@router.topic('aurora/+/+/matrix/view/set-nyan', QOS_1)
async def handle_set_nyan(message, wild1, wild2):
    matrix.user_view = AnimatedImageView('resources/img/nyan.gif', 1, 0)


@router.topic('aurora/+/+/matrix/view/text', QOS_1)
async def handle_text(message, wild1, wild2):
    matrix.user_view = ScrollingTextView(str(message.data, 'utf-8'))


@router.topic('aurora/+/+/matrix/settings', QOS_1)
async def handle_settings(message: ApplicationMessage, wild1, wild2):
    settings = json.loads(message.data)
    print("Data:" + str(settings))
    if 'brightness' in settings and 0 <= settings['brightness'] <= 100:
        matrix.matrix.brightness = settings['brightness']

