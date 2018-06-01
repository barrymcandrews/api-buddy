import json

from hbmqtt.session import ApplicationMessage
from led_matrix import matrix, configuration, views
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1
from led_matrix.router import Router
from led_matrix.views import ScrollingTextView, AnimatedImageView

config = configuration.MqttOptions
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


@router.topic('view', QOS_1)
async def handle_view(message):
    try:
        view_json = json.loads(message.data)
        matrix.user_view = await views.create_view(view_json)
    except Exception as e:
        print(e)


@router.topic('view/clear', QOS_1)
async def handle_view(message):
    matrix.user_view = None


@router.topic('view/set-nyan', QOS_1)
async def handle_set_nyan(message):
    matrix.user_view = AnimatedImageView('resources/img/nyan.gif', 1, 0)


@router.topic('view/text', QOS_1)
async def handle_text(message):
    matrix.user_view = ScrollingTextView(str(message.data, 'utf-8'))


@router.topic('settings', QOS_1)
async def handle_settings(message: ApplicationMessage):
    settings = json.loads(message.data)
    print("Data:" + str(settings))
    if 'brightness' in settings and 0 <= settings['brightness'] <= 100:
        matrix.matrix.brightness = settings['brightness']

