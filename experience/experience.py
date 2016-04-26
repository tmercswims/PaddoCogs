from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
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
        # if not message.author.bot:
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

    @commands.command(pass_context=True, aliases=["shamelist", "score"])
    async def xp(self, context, *userid: str):
        """Show the highscores"""
        file = 'data/experience/experience.json'
        experience = fileIO(file, "load")
        server = context.message.server.id
        experience = experience[server]
        if userid:
            if userid[0] in experience:
                message = '`{0} has {1} XP.`'.format(experience[userid[0]]['USERNAME'], experience[userid[0]]['TOTAL_XP'])
            else:
                message = '`\'{0}\' is not in my database.`'.format(userid[0])
        else:
            xp = sorted(experience, key=lambda x: (experience[x]['TOTAL_XP']), reverse=True)
            message = '```{0} Highscores.\n\n'.format(context.message.server.name)
            for i, userid in enumerate(xp, 1):
                if i > 15:
                    break
                message += '{0} {1} {2}\n'.format(str(i).ljust(3), str(experience[userid]['TOTAL_XP']).ljust(9), experience[userid]['USERNAME'])
            message += '```'
        await self.bot.say(message)

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def xpset(self, context, *arguments: str):
        file = 'data/experience/experience.json'
        experience = fileIO(file, "load")
        server = context.message.server.id
        if arguments:
            if arguments[0] in experience[server]:
                if arguments[1]:
                    if self.is_int(arguments[1]):
                        experience[server][arguments[0]]['TOTAL_XP'] = int(arguments[1])
                        fileIO(file, "save", experience)
                        message = '`XP set`'
                    else:
                        message = '`Value must be an integer.`'
                else:
                    message = '`Value must be an integer.`'
        await self.bot.say(message)

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def xpignore(self, context, *arguments: str):
        file = 'data/experience/experience.json'
        experience = fileIO(file, "load")
        server = context.message.server.id
        if arguments:
            if arguments[0] in experience[server]:
                if arguments[1].upper() == 'TRUE':
                    experience[server][arguments[0]]['IGNORE'] = True
                    fileIO(file, "save", experience)
                    message = '`Ignoring {0}`'.format(arguments[0])
                elif arguments[1].upper() == 'FALSE':
                    experience[server][arguments[0]]['IGNORE'] = False
                    fileIO(file, "save", experience)
                    message = '`Listening to {0}`'.format(arguments[0])
                else:
                    message = '`Value must be either True or False.`'
            else:
                message = '`Not in there yet`'
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
