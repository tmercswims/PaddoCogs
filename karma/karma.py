import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
import os
import re


class karma:
    """A cog for karma. Each server has a different list."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/karma/karma.json'
        self.settings = fileIO("data/red/settings.json", "load")

    def is_int(self, n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    async def add_karma(self, message):
            try:
                prefixes = self.settings['PREFIXES']
                content = re.sub(r"http\S+", "", message.content)
                server = message.server
                author = message.author
                valid = True
                for prefix in prefixes:
                    if content.startswith(prefix):
                        valid = False
                if valid and not author.bot:
                    data = fileIO(self.data_file, "load")
                    if server.id not in data:
                        data[server.id] = {}
                    if author.id not in data[server.id]:
                        data[server.id][author.id] = {}
                        data[server.id][author.id]['IGNORE'] = False
                        data[server.id][author.id]['KARMA'] = 0
                    if not data[server.id][author.id]['IGNORE']:
                        if author.nick is not None:
                            data[server.id][author.id]['USERNAME'] = author.nick
                        else:
                            data[server.id][author.id]['USERNAME'] = author.name
                        data[server.id][author.id]['KARMA'] += int(len(content))
                    fileIO(self.data_file, "save", data)
            except:
                pass

    @commands.group(pass_context=True, name='karma')
    async def _xp(self, context):
        """Keeps track of karma points, counted by character"""
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_xp.command(pass_context=True, name='show')
    async def _show(self, context, *username: discord.Member):
        """[@username] - shows top 15 when left empty"""
        data = fileIO(self.data_file, "load")
        server = context.message.server
        data = data[server.id]
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
        data = fileIO(self.data_file, "load")
        server = context.message.server
        if username.id in data[server.id]:
            if self.is_int(value):
                data[server.id][username.id]['KARMA'] = int(value)
                fileIO(self.data_file, "save", data)
                message = '`XP set`'
            else:
                message = '`Value must be an integer.`'
            await self.bot.say(message)

    @_xp.command(pass_context=True, name='ignore')
    async def _ignore(self, context):
        """Do this if you don't want to receive any karma."""
        data = fileIO(self.data_file, "load")
        server = context.message.server
        author = context.message.author
        if author.id in data[server.id]:
            value = data[server.id][author.id]['IGNORE']
            print(value)
            if not value:
                data[server.id][author.id]['IGNORE'] = True
                message = '`Ignoring you`'
            else:
                data[server.id][author.id]['IGNORE'] = False
                message = '`Tracking you`'
            fileIO(self.data_file, "save", data)
            await self.bot.say(message)

    @_xp.command(pass_context=True, name='clear')
    @checks.mod_or_permissions(manage_roles=True)
    async def _clear(self, context):
        """Clears the karma list of the current server."""
        data = fileIO(self.data_file, "load")
        server = context.message.server
        if server.id in data:
            data[server.id] = {}
            fileIO(self.data_file, "save", data)
            await self.bot.say('`List cleared`')


def check_folder():
    if not os.path.exists("data/karma"):
        print("Creating data/karma folder...")
        os.makedirs("data/karma")


def check_file():
    data = {}
    f = "data/karma/karma.json"
    if not fileIO(f, "check"):
        print("Creating default karma.json...")
        fileIO(f, "save", data)


def setup(bot):
    check_folder()
    check_file()
    n = karma(bot)
    bot.add_listener(n.add_karma, "on_message")
    bot.add_cog(n)
