from .utils.dataIO import fileIO
from discord.ext import commands
from .utils import checks
import datetime
import asyncio
import discord
import time
import os

class Statistics:
    """
    Statistics
    """
    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO('data/statistics/settings.json', 'load')
        self.sent_messages = self.settings['SENT_MESSAGES']
        self.received_messages = self.settings['RECEIVED_MESSAGES']
        self.refresh_rate = self.settings['REFRESH_RATE']

    async def _int(self, n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    @commands.command()
    async def stats(self):
        """
        Retreive statistics
        """
        message = await self.retrieve_statistics()
        await self.bot.say(message)

    @commands.command()
    async def statsrefresh(self, seconds: int):
        """
        Set the refresh rate by which the statistics are updated

        Example: [p]statsrefresh 42

        Default: 5
        """
        if await self._int(seconds):
            if seconds < 5:
                message = '`I can\'t do that, the refresh rate has to be above 5 seconds`'
            else:
                self.refresh_rate = seconds
                self.settings['REFRESH_RATE'] = self.refresh_rate
                fileIO('data/statistics/settings.json', 'save', self.settings)
                message = '`Changed refresh rate to {} seconds`'.format(self.refresh_rate)
        await self.bot.say(message)

    @commands.command(no_pm=True)
    @checks.serverowner_or_permissions(manage_server=True)
    async def statschannel(self, *channel: discord.Channel):
        """
        Set the channel to which the bot will sent its continues updates.
        Example: [p]statschannel #statistics
        """
        if len(channel) > 0:
            self.settings['CHANNEL_ID'] = str(channel[0].id)
            fileIO('data/statistics/settings.json', 'save', self.settings)
            message = 'Channel set to {}'.format(channel[0].mention)
        elif not self.settings['CHANNEL_ID']:
            message = 'No channel set!'
        else:
            channel = discord.utils.get(self.bot.get_all_channels(), id=self.settings['CHANNEL_ID'])
            message = 'Current channel is {}'.format(channel.mention)
        await self.bot.say(message)

    async def retrieve_statistics(self):
        name = self.bot.user.name
        uptime = abs(self.bot.uptime - int(time.perf_counter()))
        up = datetime.timedelta(seconds=uptime)
        days = up.days
        hours = int(up.seconds/3600)
        minutes = int(up.seconds%3600/60)
        avg_sent = round(self.sent_messages / uptime, 3)
        avg_recv = round(self.received_messages / uptime, 3)
        users = str(len(set(self.bot.get_all_members())))
        servers = str(len(self.bot.servers))
        text_channels = 0
        voice_channels = 0
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.text:
                text_channels += 1
            elif channel.type == discord.ChannelType.voice:
                voice_channels += 1
        channels = text_channels + voice_channels
        message = '**{}** has been up for **{} days, {} hours, and {} minutes**'.format(name, str(days), str(hours), str(minutes))
        message+= '\n\n'
        message+= 'Connected to **{}** servers'.format(servers)
        message+= '\n'
        message+= 'Seen **{}** users'.format(users)
        message+= '\n'
        message+= 'In **{}** channels (**{}** text, **{}** voice)'.format(str(channels), str(text_channels), str(voice_channels))
        message+= '\n'
        message+= '**{}** messages received (**{}** per second) and **{}** messages sent (**{}** per second)'.format(str(self.received_messages), str(avg_recv), str(self.sent_messages), str(avg_sent))
        message+= '\n'
        message+= '**{}** active cogs with **{}** commands'.format(str(len(self.bot.cogs)), str(len(self.bot.commands)))
        message+= '\n'
        message+= 'API version **{}**'.format(discord.__version__)
        return message

    async def incoming_messages(self, message):
        if message.author.id == self.bot.user.id:
            self.sent_messages += 1
        else:
            self.received_messages += 1
        self.settings['SENT_MESSAGES'] = self.sent_messages
        self.settings['RECEIVED_MESSAGES'] = self.received_messages
        fileIO('data/statistics/settings.json', 'save', self.settings)

    async def reload_stats(self):
        await asyncio.sleep(30)
        while self == self.bot.get_cog('Statistics'):
            if self.settings['CHANNEL_ID']:
                msg = await self.retrieve_statistics()
                channel = discord.utils.get(self.bot.get_all_channels(), id=self.settings['CHANNEL_ID'])
                messages = False
                async for message in self.bot.logs_from(channel, limit=1):
                    messages = True
                    if message.author.name == self.bot.user.name:
                        await self.bot.edit_message(message, msg)
                if not messages:
                    await self.bot.send_message(channel, msg)
            else:
                pass
            await asyncio.sleep(self.refresh_rate)

def check_folder():
    if not os.path.exists("data/statistics"):
        print("Creating data/statistics folder...")
        os.makedirs("data/statistics")

def check_file():
    data = {}
    data['CHANNEL_ID'] = ''
    data['SENT_MESSAGES'] = 0
    data['RECEIVED_MESSAGES'] = 0
    data['REFRESH_RATE'] = 5
    f = "data/statistics/settings.json"
    if not fileIO(f, "check"):
        print("Creating default settings.json...")
        fileIO(f, "save", data)

def setup(bot):
    check_folder()
    check_file()
    n = Statistics(bot)
    bot.add_cog(n)
    bot.add_listener(n.incoming_messages, "on_message")
    bot.loop.create_task(n.reload_stats())
