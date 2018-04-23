from typing import List
from hbmqtt.session import ApplicationMessage


class Topic(object):
    def __init__(self, topic, qos=None, handler=None):
        self.topic = topic
        self.qos = qos
        self.handler = handler
        self.topic_list = topic.split('/')

    # Returns None if not a match
    # Returns list of wildchars if True
    def find_wildchars(self, other_list):
        wc = []
        min_length = min(len(self.topic_list), len(other_list))
        for i in range(0, min_length):
            this_item = self.topic_list[i]
            other_item = other_list[i]
            if this_item == '#':
                return wc
            elif this_item == "+":
                wc.append(other_item)
            elif this_item != other_item:
                return None
        return wc if len(self.topic_list) == len(other_list) else None


class Router(object):
    def __init__(self, client):
        self.client = client
        self.topics: List[Topic] = []

    async def push(self, message: ApplicationMessage):
        msg_topic_list = message.topic.split('/')

        for my_topic in self.topics:
            wc = my_topic.find_wildchars(msg_topic_list)
            if wc is not None:
                print("Message recieved. Topic:  " + message.topic)
                await my_topic.handler(message, *wc)

    # Decorator
    def topic(self, topic, qos):
        def decorator(handler):
            self.topics.append(Topic(topic, qos, handler))
            return handler
        return decorator


