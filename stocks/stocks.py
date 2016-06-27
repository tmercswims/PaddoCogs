import aiohttp
from discord.ext import commands

class Stocks:
    def __init__(self, bot):
        self.bot = bot
        self.url_base = "http://finance.yahoo.com/webservice/v1/symbols/{}/quote?"
        self.payload = {}
        self.payload['format'] = 'json'
        self.payload['view'] = 'detail'

    @commands.command(pass_context=True, name='stocks', aliases=['stock'])
    async def _stocks(self, context, symbol: str):
        """
            Get the latest from your favorite stocks.

            Symbol must be precise i.e ^IXIC for NASDAQ, EURGBP=X for EURO/GBP
            For multiple results seperate by comma i.e ^IXIC,EURGBP=X,DOW,...,...
        """
        payload = self.payload
        url = self.url_base.format(symbol.replace(', ', ','))
        headers = {'user-agent': 'Red-cog/1.0.0'}
        conn = aiohttp.TCPConnector(verify_ssl=False)
        session = aiohttp.ClientSession(connector=conn)
        async with session.get(url, params=payload, headers=headers) as r:
            result = await r.json()
        session.close()
        message = ''
        if result['list']['meta']['count'] > 0:
            for resource in result['list']['resources']:
                res = resource['resource']['fields']
                name =  res['name'].replace('&amp;', '&')
                symbol = res['symbol']
                price = res['price']
                day_low = res['day_low']
                day_high = res['day_high']
                change = res['change']
                change_percentage = res['chg_percent']
                if change < 0:
                    change = '▼ {}'.format(str(change))
                else:
                    change = '▲ {}'.format(str(change))
                if change_percentage < 0:
                    change = '▼ {}'.format(str(change_percentage))
                else:
                    change = '▲ {}'.format(str(change_percentage))
                message+= '**{}** ({})\n**POINTS**: *{}* `{} ({}%)`\n**HIGH/LOW**: *{} - {}*\n\n'.format(name, symbol, price, change, change_percentage, day_low, day_high)
        else:
            message = 'Could not find symbol'
        await self.bot.say(message)

def setup(bot):
    n = Stocks(bot)
    bot.add_cog(n)
