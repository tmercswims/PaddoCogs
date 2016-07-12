import os
import re
import aiohttp
from .utils import checks
from discord.ext import commands
from .utils.dataIO import fileIO
from __main__ import send_cmd_help

try:
    import xmltodict
    xmltodict_lib = True
except:
    xmltodict_lib = False

class Goodreads:
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/goodreads/settings.json'
        self.gateway = 'https://www.goodreads.com/book/{}.xml?'
        self.payload = {}
        self.key = fileIO(self.settings_file, "load")['API_KEY']

    async def _get_query(self, payload, gateway):
        headers = {'user-agent': 'Red-cog/1.0'}
        conn = aiohttp.TCPConnector(verify_ssl=False)
        session = aiohttp.ClientSession(connector=conn)
        async with session.get(gateway, params=payload, headers=headers) as r:
            data = await r.text()
        session.close()
        return data

    async def _xml_parser(self, xml):
        return xmltodict.parse(xml)

    async def _query_search(self, query):
        payload = self.payload
        payload['title'] = query
        payload['key'] = self.key
        gateway = self.gateway.format('title')
        result = await self._get_query(payload, gateway)
        parse = await self._xml_parser(result)
        if 'GoodreadsResponse' in parse:
            book = parse['GoodreadsResponse']['book']
            book_url = book['url']
            book_title = book['title']
            if book_title == None:
                book_title = 'No title'
            book_rating = book['average_rating']
            if book_rating == None:
                book_rating = 'No ratings'
            book_published = book['work']['original_publication_year']['#text']
            if book_published == None:
                book_published = 'No information'
            if book['description'] != None:
                book_description =  re.sub('<.*?>', '', book['description'].replace('<br>', '\n'))
            else:
                book_description = 'No description available'
            if len(book_description) > 600:
                book_description = book_description[0:500-3] + '...'
            authors = ''
            if len(book['authors']['author']) == 9:
                authors += '{} ({})'.format(book['authors']['author']['name'], book['authors']['author']['average_rating'])
            else:
                for author in book['authors']['author']:
                    authors+= '{} ({}), '.format(author['name'], author['average_rating'])
                authors = authors[:-2]
            backtrack = '```{}\n\nPublished: {}\nAuthors: {}\nRating: {}\n\n{}\n\nRead more at: {}```'.format(book_title, book_published, authors, book_rating, book_description, book_url)
            return backtrack
        else:
            return '**I couldn\'t find that!**'

    @commands.command(pass_context=True, name='goodreads', aliases=['gr'])
    async def _goodreads(self, context, *, search : str):
        if search:
            if self.key:
                message = await self._query_search(search)
            else:
                message = 'No API key set!'
            await self.bot.say('{}'.format(message))
        else:
            await send_cmd_help(context)

    @commands.command(pass_context=True, name='goodreadsapi')
    @checks.is_owner()
    async def _api(self, context, key: str):
        """Set an API key for this cog. Get one at: """
        data = fileIO(self.settings_file, "load")
        data['API_KEY'] = key
        self.key = key
        message = 'API Key set'
        fileIO(self.settings_file, "save", data)
        await self.bot.say('*{}*'.format(message))

def check_folder():
    if not os.path.exists("data/goodreads"):
        print("Creating data/goodreads folder...")
        os.makedirs("data/goodreads")

def check_file():
    data = {}
    data['API_KEY'] = ''
    f = "data/goodreads/settings.json"
    if not fileIO(f, "check"):
        print("Creating default settings.json...")
        fileIO(f, "save", data)

def setup(bot):
    if xmltodict_lib:
        check_folder()
        check_file()
        n = Goodreads(bot)
        bot.add_cog(n)
    else:
        raise RuntimeError('You need to run \'pip3 install xmltodict\' to use this cog.')
