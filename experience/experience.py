import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
import os
import re


class Experience:
    """A cog for highscores among members. Each server has a different list."""

    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/red/settings.json", "load")

    def is_int(self, n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    async def add_xp(self, message):
            try:
                prefixes = self.settings['PREFIXES']
                content = re.sub(r"http\S+", "", message.content)
                valid = True

                for prefix in prefixes:
                    if prefix in content[0:5]:
                        valid = False
                if valid:
                    file = 'data/experience/experience.json'
                    experience = fileIO(file, "load")
                    server = message.server.id
                    author_mention = message.author.mention
                    author = message.author.name
                    if server not in experience:
                        experience[server] = {}
                    if author_mention not in experience[server]:
                        experience[server][author_mention] = {}
                        experience[server][author_mention]['IGNORE'] = False
                        experience[server][author_mention]['TOTAL_XP'] = 0
                    if not experience[server][author_mention]['IGNORE']:
                        experience[server][author_mention]['USERNAME'] = author
                        experience[server][author_mention]['TOTAL_XP'] += int(len(content))
                    fileIO(file, "save", experience)
            except:
                pass

    @commands.group(pass_context=True)
    async def xp(self, context):
        """Keeps track of xp, counted by character"""
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @xp.command(pass_context=True)
    async def show(self, context, *user: str):
        """[@username] - shows top 15 when left empty"""
        file = 'data/experience/experience.json'
        experience = fileIO(file, "load")
        server = context.message.server.id
        experience = experience[server]
        if user:

            user_patch = user[0].replace('!', '')
            if user_patch in experience:
                message = '`{0} has {1} XP.`'.format(experience[user_patch]['USERNAME'], experience[user_patch]['TOTAL_XP'])
            else:
                message = '`\'{0}\' is not in my database.`'.format(user_patch)
        else:
            xp = sorted(experience, key=lambda x: (experience[x]['TOTAL_XP']), reverse=True)
            message = '```{0} Highscores.\n\n'.format(context.message.server.name)
            for i, userid in enumerate(xp, 1):
                if i > 15:
                    break
                message += '{0} {1} {2}\n'.format(str(i).ljust(3), str(experience[userid]['TOTAL_XP']).ljust(9), experience[userid]['USERNAME'])
            message += '```'
        await self.bot.say(message)

    @xp.command(pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def set(self, context, username: str, value: str):
        """[@username] [n]"""
        file = 'data/experience/experience.json'
        experience = fileIO(file, "load")
        server = context.message.server.id
        user_patch = username.replace('!', '')
        if user_patch in experience[server]:
            if self.is_int(value):
                experience[server][user_patch]['TOTAL_XP'] = int(value)
                fileIO(file, "save", experience)
                message = '`XP set`'
            else:
                message = '`Value must be an integer.`'
        if len(message) > 0:
            await self.bot.say(message)

    @xp.command(pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def ignore(self, context, username: str, value: str):
        """[@username] [true|false]"""
        file = 'data/experience/experience.json'
        experience = fileIO(file, "load")
        server = context.message.server.id
        user_patch = username.replace('!', '')
        if user_patch in experience[server]:
            if value.upper() == 'TRUE':
                experience[server][user_patch]['IGNORE'] = True
                fileIO(file, "save", experience)
                message = '`Ignoring`'
            elif value.upper() == 'FALSE':
                experience[server][user_patch]['IGNORE'] = False
                fileIO(file, "save", experience)
                message = '`Done`'
            else:
                message = '`Value must be either True or False.`'
        if len(message) > 0:
            await self.bot.say(message)


def check_folder():
    if not os.path.exists("data/experience"):
        print("Creating data/experience folder...")
        os.makedirs("data/experience")


def check_file():
    experience = {}
    f = "data/experience/experience.json"
    if not fileIO(f, "check"):
        print("Creating default experience.json...")
        fileIO(f, "save", experience)


def setup(bot):
    check_folder()
    check_file()
    n = Experience(bot)
    bot.add_listener(n.add_xp, "on_message")
    bot.add_cog(n)
