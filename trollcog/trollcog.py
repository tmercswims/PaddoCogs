import os
import time
import random
import asyncio
import discord
from .utils import checks
from discord.ext import commands
from cogs.utils.dataIO import dataIO

cog_name = 'trollcog'
data_name = 'optout'

class Trollcog:
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/{}/{}.json'.format(cog_name, data_name)
        data = dataIO.load_json(self.data_file)
        self.timer = data['TROLL_TIMER']
        self.cooldown_timer = data['COOLDOWN_TIMER']
        self.cooldown = {}

    @commands.command(pass_context=True, no_pm=True, name='troggle')
    async def _troggle(self, context):
        """Toggle if you want to opt-out of trolling"""
        author = context.message.author
        data = dataIO.load_json(self.data_file)
        if author.id not in data:
            data[author.id] = False
            message = 'You opted out.'
        elif data[author.id]:
            data[author.id] = False
            message = 'You opted out.'
        else:
            data[author.id] = True
            message = 'You opted in.'
        dataIO.save_json(self.data_file, data)
        await self.bot.say(message)

    @commands.command(pass_context=True, no_pm=True, name='trogglecooldown')
    @checks.serverowner_or_permissions(administrator=True)
    async def _trogglecooldown(self, context, seconds: int):
        """Sets the timer for how often a person can be trolled. Default: 10800 (3 hours)"""
        data = dataIO.load_json(self.data_file)
        if seconds < 3600:
            message = 'At least an hour!'
        else:
            self.cooldown_timer = seconds
            data['COOLDOWN_TIMER'] = seconds
            message = 'Cooldown timer set to {} seconds'.format(seconds)
        dataIO.save_json(self.data_file, data)
        await self.bot.say(message)

    @commands.command(pass_context=True, no_pm=True, name='troggletimer')
    @checks.is_owner() 
    async def _troggletimer(self, context, seconds: int):
        """Sets the timer for how often trolls happen. Default: 960 (16 minutes)"""
        data = dataIO.load_json(self.data_file)
        if seconds < 240:
            message = 'At least 4 minutes!'
        else:
            self.timer = seconds
            data['TROLL_TIMER'] = seconds
            message = 'Troll timer set to {} seconds'.format(seconds)
        dataIO.save_json(self.data_file, data)
        await self.bot.say(message)

    async def coolloop(self):
        await self.bot.wait_until_ready()
        while self == self.bot.get_cog('Trollcog'):
            l = [member for member in self.cooldown if (int('{0:.0f}'.format(time.time())) - int(self.cooldown[member]) > self.cooldown_timer)]
            for member in l:
                del self.cooldown[member]
            await asyncio.sleep(60)

    async def trolloop(self):
        await self.bot.wait_until_ready()
        while self == self.bot.get_cog('Trollcog'):
            data = dataIO.load_json(self.data_file)
            channel = random.choice([channel for channel in self.bot.get_all_channels() if (channel.type is discord.ChannelType.text)])
            member = random.choice([member for member in channel.server.members if (member.status is discord.Status.online or member.status is discord.Status.offline and not member.bot)])
            if member.id not in self.cooldown:
                if member.id not in data or data[member.id]:
                    if channel.permissions_for([member for member in channel.server.members if (self.bot.user.name in member.name)][0]).send_messages:
                        if channel.permissions_for(member).read_messages:
                            message = await self.bot.send_message(channel, '{} :upside_down:'.format(member.mention))
                            await self.bot.delete_message(message)
                            self.cooldown[member.id] = int('{0:.0f}'.format(time.time()))
                            await asyncio.sleep(self.timer)
            await asyncio.sleep(5)

def check_folder():
    if not os.path.exists('data/{}'.format(cog_name)):
        print('Creating data/{}'.format(cog_name))
        os.makedirs('data/{}'.format(cog_name))

def check_file():
    data = {}
    data['COOLDOWN_TIMER'] = 10800
    data['TROLL_TIMER'] = 960
    f = 'data/{}/{}.json'.format(cog_name, data_name)
    if dataIO.is_valid_json(f) is False:
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    n = Trollcog(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.trolloop())
    bot.loop.create_task(n.coolloop())
