import requests
from requests.auth import HTTPDigestAuth
import json
import time


def createXML():
    url = "https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=5cb5f7386c994da78df77cefb4b29e25"
    my_response = requests.get(url)

    if my_response.ok:
        json_data = json.loads(my_response.content)

        articles = json_data['articles']
        for index, val in enumerate(articles):
            currentArticle = json_data["articles"][index]["title"].encode('utf-8').strip()
            with open("/tmp/led-source-news", 'w') as f:
                f.write('<message type="scroll" color="#FF0028" style="bold">' + str(currentArticle) + '</message>')
                f.close()
                time.sleep(120)
    time.sleep(10)


while True:
    createXML()

