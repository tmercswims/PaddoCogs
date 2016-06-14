import discord
import os
from discord.ext import commands
from .utils.dataIO import fileIO
from __main__ import send_cmd_help

class BarPM:
    def __init__(self, bot):
        self.bot = bot
        self.drinkers = 'data/barpm/drinkers.json'
        self.settings = fileIO("data/red/settings.json", "load")

        self.beverages = {}

        self.beverages['beer'] = {}
        self.beverages['beer']['NAME'] = 'Beer'
        self.beverages['beer']['EMOJI'] = 'Prost :beers:!'
        self.beverages['wine'] = {}
        self.beverages['wine']['NAME'] = 'wine'
        self.beverages['wine']['EMOJI'] = ':wine_glass:'
        self.beverages['cocktail'] = {}
        self.beverages['cocktail']['NAME'] = 'Cocktail'
        self.beverages['cocktail']['EMOJI'] = ':cocktail:'
        self.beverages['lemonade'] = {}
        self.beverages['lemonade']['NAME'] = 'Lemonade'
        self.beverages['lemonade']['EMOJI'] = ':tropical_drink:'
        self.beverages['champagne'] = {}
        self.beverages['champagne']['NAME'] = 'Champagne'
        self.beverages['champagne']['EMOJI'] = ':champagne:'
        self.beverages['tea'] = {}
        self.beverages['tea']['NAME'] = 'Tea'
        self.beverages['tea']['EMOJI'] = ':tea:'
        self.beverages['coffee'] = {}
        self.beverages['coffee']['NAME'] = 'Coffee'
        self.beverages['coffee']['EMOJI'] = ':coffee:'
        self.beverages['hotchoc'] = {}
        self.beverages['hotchoc']['NAME'] = 'Hot Chocolate'
        self.beverages['hotchoc']['EMOJI'] = ':coffee:'
        self.beverages['aloe'] = {}
        self.beverages['aloe']['NAME'] = 'Aloe Vera'
        self.beverages['aloe']['EMOJI'] = ':sunglasses:'
        self.beverages['noots'] = {}
        self.beverages['noots']['NAME'] = 'Noots'
        self.beverages['noots']['EMOJI'] = ':penguin:'

    async def listener(self, message):
        content = message.content
        author = message.author
        prefixes = self.settings['PREFIXES']
        valid = True
        for prefix in prefixes:
            if content.startswith(prefix):
                valid = False
        if valid and not author.bot:
            for beverage in self.beverages:
                if self.beverages[beverage]['NAME'].lower() in content.lower():
                    data = fileIO(self.drinkers, 'load')
                    for drinker in data:
                        if str(drinker) != str(author.id):
                            if beverage in data[drinker]['SUBS']:
                                beverage_name = self.beverages[beverage]['NAME']
                                beverage_emoji = self.beverages[beverage]['EMOJI']
                                message = '{} wants to give you a {}! {}'.format(author.name, beverage_name, beverage_emoji)
                                user = discord.utils.get(self.bot.private_channels, user__id=str(drinker))
                                await self.bot.send_message(user, message)

    @commands.group(pass_context=True, no_pm=True, name='bar', aliases=['pub'])
    async def _bar(self, context):
        """Choose your poison"""
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_bar.command(pass_context=True, no_pm=True, name='menu', aliases=['list'])
    async def _menu(self, context):
        """List of available beverages"""
        message = 'Available beverages\n\n'
        for i, beverage in enumerate(self.beverages, 1):
            message += '{:<3}{:<10}\n'.format(str(i), self.beverages[beverage]['NAME'])
        await self.bot.say('```{}```'.format(message))

    @_bar.command(pass_context=True, no_pm=True, name='subscribe', aliases=['sub'])
    async def _subscribe(self, context, beverage: str):
        """Subscribe to a beverage"""
        author = context.message.author
        beverage = beverage.lower()
        data = fileIO(self.drinkers, 'load')
        for item in self.beverages:
            if beverage in self.beverages[item]['NAME'].lower():
                if author.id not in data:
                    data[author.id] = {}
                    data[author.id]['SUBS'] = []
                if not item in data[author.id]['SUBS']:
                    data[author.id]['SUBS'].append(item)
                    message = '**I will serve this from now on.**'
                else:
                    message = '**I am already serving you this.**'
                fileIO(self.drinkers, 'save', data)
                break
            else:
                message = '**I do not serve this beverage.**'
        await self.bot.say(message)

    @_bar.command(pass_context=True, no_pm=True, name='unsubscribe', aliases=['unsub'])
    async def _unsubscribe(self, context, beverage):
        """Subscribe to a beverage"""
        author = context.message.author
        beverage = beverage.lower()
        data = fileIO(self.drinkers, 'load')
        for item in self.beverages:
            if beverage in self.beverages[item]['NAME'].lower():
                if author.id in data:
                    if item in data[author.id]['SUBS']:
                        print(data[author.id]['SUBS'])
                        i = data[author.id]['SUBS'].index(item)
                        del data[author.id]['SUBS'][i]
                        fileIO(self.drinkers, 'save', data)
                        message = '**I will stop serving you this.**'
                    else:
                        message = '**I am not serving this beverage to you.**'
                else:
                    message = '**I am not serving you anything yet.**'

                break
            else:
                message = '**I do not serve this beverage.**'
        await self.bot.say(message)

def check_folder():
    if not os.path.exists('data/barpm'):
        print('Creating data/barpm folder...')
        os.makedirs('data/barpm')

def check_file():
    data = {}
    f = 'data/barpm/drinkers.json'
    if not fileIO(f, 'check'):
        print('Creating default drinkers.json...')
        fileIO(f, 'save', data)

def setup(bot):
    check_folder()
    check_file()
    n = BarPM(bot)
    bot.add_listener(n.listener, 'on_message')
    bot.add_cog(n)
