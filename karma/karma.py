import discord
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os
import re


class karma:
    """A cog for karma. Each server has a different list."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/karma/karma.json'
        self.settings = dataIO.load_json('data/red/settings.json')

    def is_int(self, n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    async def add_karma(self, message):
            author = message.author
            if not author.bot:
                prefixes = self.settings['PREFIXES']
                server = message.server
                content = re.sub(r"http\S+", "", message.content)
                filename = 'data/karma/{}.json'.format(server.id)
                if not dataIO.is_valid_json(filename):
                    data = {}
                    dataIO.save_json(filename)
                else:
                    data = dataIO.load_json(filename)
                valid = True
                for prefix in prefixes:
                    if content.startswith(prefix):
                        valid = False
                if valid:
                    if author.id not in data:
                        data[author.id] = {}
                        data[author.id]['IGNORE'] = False
                        data[author.id]['KARMA'] = 0
                        data[author.id]['USERNAME'] = author.display_name
                    data[author.id]['KARMA'] += int(len(content))
                dataIO.save_json(filename, data)

    @commands.group(pass_context=True, name='karma')
    async def _xp(self, context):
        """Keeps track of karma points, counted by character"""
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_xp.command(pass_context=True, name='show')
    async def _show(self, context, *username: discord.Member):
        """[@username] - shows top 15 when left empty"""
        server = context.message.server
        filename = 'data/karma/{}.json'.format(server.id)
        if dataIO.is_valid_json(filename):
            data = dataIO.load_json(filename)
        if username:
            username = username[0]
            if username.id in data:
                message = '`{0} has {1} karma points.`'.format(data[username.id]['USERNAME'], data[username.id]['KARMA'])
            else:
                message = '`\'{0}\' is not in my database.`'.format(username.name)
        else:
            karma = sorted(data, key=lambda x: (data[x]['KARMA']), reverse=True)
            message = '```Karma of {0}\n\n'.format(server.name)
            for i, userid in enumerate(karma, 1):
                if i > 15:
                    break
                message += '{:<5}{:<10}{:<10}\n'.format(str(i)+')', str(data[userid]['KARMA']), data[userid]['USERNAME'])
            message += '```'
        await self.bot.say(message)

    @_xp.command(pass_context=True, name='set')
    @checks.mod_or_permissions(manage_roles=True)
    async def _set(self, context, username: discord.Member, value: str):
        """[@username] [n]"""
        server = context.message.server
        filename = 'data/karma/{}.json'.format(server.id)
        if dataIO.is_valid_json(filename):
            data = dataIO.load_json(filename)
            if username.id in data:
                if self.is_int(value):
                    data[username.id]['KARMA'] = int(value)
                    dataIO.save_json(filename, data)
                    message = '`XP set`'
                else:
                    message = '`Value must be an integer.`'
                await self.bot.say(message)

    @_xp.command(pass_context=True, name='ignore')
    async def _ignore(self, context):
        """Do this if you don't want to receive any karma."""
        server = context.message.server
        author = context.message.author
        filename = 'data/karma/{}.json'.format(server.id)
        if dataIO.is_valid_json(filename):
            data = dataIO.load_json(filename)
            if author.id in data:
                value = data[author.id]['IGNORE']
                if not value:
                    data[author.id]['IGNORE'] = True
                    message = '`Ignoring you`'
                else:
                    data[author.id]['IGNORE'] = False
                    message = '`Tracking you`'
                dataIO.save_json(filename, data)
                await self.bot.say(message)

    @_xp.command(pass_context=True, name='clear')
    @checks.mod_or_permissions(manage_roles=True)
    async def _clear(self, context):
        """Clears the karma list of the current server."""
        server = context.message.server
        filename = 'data/karma/{}.json'.format(server.id)
        if dataIO.is_valid_json(filename):
            data = dataIO.load_json(filename)
            data = {}
            dataIO.save_json(filename, data)

            await self.bot.say('`List cleared`')


def check_folder():
    if not os.path.exists("data/karma"):
        print("Creating data/karma folder...")
        os.makedirs("data/karma")


def check_file():
    data = {}
    f = "data/karma/karma.json"
    if not dataIO.is_valid_json(f):
        print("Creating default karma.json...")
        dataIO.is_valid_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    n = karma(bot)
    bot.add_listener(n.add_karma, "on_message")
    bot.add_cog(n)
