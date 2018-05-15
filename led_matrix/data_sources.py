import asyncio
import aiohttp
from abc import abstractmethod


class RestApi(object):

    def __init__(self, update_interval=600):
        self.response = None
        self.update_interval = update_interval
        self.future = asyncio.ensure_future(self.update())
        self.initialized = asyncio.Event()
        self.initialized.clear()

    def __del__(self):
        self.future.cancel()

    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def text(self) -> str:
        pass

    async def update(self):
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url()) as resp:
                    self.response = await resp.json()
                    self.initialized.set()
            await asyncio.sleep(self.update_interval)


class WeatherApi(RestApi):
    api_key: str = 'bb354419bad726205a58624ce10ed5ab'

    def url(self):
        return 'http://api.openweathermap.org/data/2.5/weather?q=Pittsburgh,us&appid=' + WeatherApi.api_key

    def text(self):
        city = self.response['name']
        temp = self.response['main']['temp']
        desc = self.response['weather'][0]['description']
        return 'Weather in ' + str(city) + ':     ' + str(temp) + ' Kelvin     ' + str(desc)


class NewsApi(RestApi):
    api_key: str = 'add7ba23208849279c9d66397dfe480a'

    def url(self):
        return 'https://newsapi.org/v2/top-headlines?country=us&apikey=' + NewsApi.api_key

    def text(self):
        top_headline = self.response['articles'][0]['title']
        return 'Top News:     ' + str(top_headline)


