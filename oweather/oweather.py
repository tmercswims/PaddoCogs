from discord.ext import commands
from cogs.utils.dataIO import dataIO
import aiohttp
import os
from .utils import checks
import datetime
import discord


class Weather:
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/weather/weather.json'

    async def _get_local_time(self, lat, lng):
        settings = dataIO.load_json(self.settings_file)
        if 'TIME_API_KEY' in settings:
            api_key = settings['TIME_API_KEY']
            if api_key != '':
                payload = {'format': 'json', 'key': api_key, 'by': 'position', 'lat': lat, 'lng': lng}
                url = 'http://api.timezonedb.com/v2/get-time-zone?'
                headers = {'user-agent': 'Red-cog/1.0'}
                conn = aiohttp.TCPConnector(verify_ssl=False)
                session = aiohttp.ClientSession(connector=conn)
                async with session.get(url, params=payload, headers=headers) as r:
                    parse = await r.json()
                session.close()
                if parse['status'] == 'OK':
                    return datetime.datetime.fromtimestamp(int(parse['timestamp'])-7200).strftime('%Y-%m-%d %H:%M')
        return

    @commands.command(pass_context=True, name='weather', aliases=['we'])
    async def _weather(self, context, *arguments: str):
        """Get the weather!"""
        settings = dataIO.load_json(self.settings_file)
        api_key = settings['WEATHER_API_KEY']
        if len(arguments) == 0:
            message = 'No location provided.'
        elif api_key != '':
            try:
                payload = {'q': " ".join(arguments), 'appid': api_key}
                url = 'http://api.openweathermap.org/data/2.5/weather?'
                headers = {'user-agent': 'Red-cog/1.0'}
                conn = aiohttp.TCPConnector(verify_ssl=False)
                session = aiohttp.ClientSession(connector=conn)
                async with session.get(url, params=payload, headers=headers) as r:
                    parse = await r.json()
                session.close()
                lat = parse['coord']['lat']
                lng = parse['coord']['lon']
                local_time = await self._get_local_time(lat, lng)
                celcius = round(int(parse['main']['temp'])-273)+1
                fahrenheit = round(int(parse['main']['temp'])*9/5-459)+2
                temperature = '{0} Celsius / {1} Fahrenheit'.format(celcius, fahrenheit)
                humidity = str(parse['main']['humidity']) + '%'
                pressure = str(parse['main']['pressure']) + ' hPa'
                wind_kmh = str(round(parse['wind']['speed'] * 3.6)) + ' km/h'
                wind_mph = str(round(parse['wind']['speed'] * 2.23694)) + ' mph'
                clouds = parse['weather'][0]['description'].title()
                icon = parse['weather'][0]['icon']
                name = parse['name'] + ', ' + parse['sys']['country']
                city_id = parse['id']
                em = discord.Embed(title='Weather in {} - {}'.format(name, local_time), color=discord.Color.blue(), description='\a\n', url='https://openweathermap.org/city/{}'.format(city_id))
                em.add_field(name='**Conditions**', value=clouds)
                em.add_field(name='**Temperature**', value=temperature)
                em.add_field(name='\a', value='\a')
                em.add_field(name='**Wind**', value='{} / {}'.format(wind_kmh, wind_mph))
                em.add_field(name='**Pressure**', value=pressure)
                em.add_field(name='**Humidity**', value=humidity)
                em.set_thumbnail(url='https://openweathermap.org/img/w/{}.png'.format(icon), width=50, height=50)
                em.add_field(name='\a', value='\a')
                em.set_footer(text='Weather data provided by OpenWeatherMap', icon_url='http://openweathermap.org/themes/openweathermap/assets/vendor/owm/img/icons/logo_16x16.png')
                await self.bot.say(embed=em)
            except KeyError:
                message = 'Location not found.'
                await self.bot.say('```{}```'.format(message))
        else:
            message = 'No API key set. Get one at http://openweathermap.org/'
            await self.bot.say('```{}```'.format(message))

    @commands.command(pass_context=True, name='weatherkey')
    @checks.is_owner()
    async def _weatherkey(self, context, arguments: str):
        """Acquire a key from  http://openweathermap.org/"""
        settings = dataIO.load_json(self.settings_file)
        if arguments:
            settings['WEATHER_API_KEY'] = arguments[0]
            dataIO.save_json(self.settings_file, settings)

    @commands.command(pass_context=True, name='timekey')
    @checks.is_owner()
    async def _timekey(self, context, *arguments: str):
        """Acquire a key from https://timezonedb.com/api"""
        settings = dataIO.load_json(self.settings_file)
        if arguments:
            settings['TIME_API_KEY'] = arguments[0]
            dataIO.save_json(self.settings_file, settings)


def check_folder():
    if not os.path.exists("data/weather"):
        print("Creating data/weather folder...")
        os.makedirs("data/weather")


def check_file():
    weather = {}
    weather['WEATHER_API_KEY'] = ''
    weather['TIME_API_KEY'] = ''

    f = "data/weather/weather.json"
    if not dataIO.is_valid_json(f):
        print("Creating default weather.json...")
        dataIO.save_json(f, weather)


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Weather(bot))
