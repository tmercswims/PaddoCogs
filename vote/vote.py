from discord.ext import commands
from .utils.dataIO import fileIO
from __main__ import send_cmd_help
from time import time
import os


class Vote:
    """Le poll cog. Does conflict with Red's default poll."""
    def __init__(self, bot):
        self.bot = bot
        self.poll_data = 'data/vote/vote.json'

    @commands.group(pass_context=True, no_pm=True)
    async def vote(self, context):
        settings = fileIO(self.poll_data, "load")
        channel = context.message.channel.id
        if channel in settings and context.invoked_subcommand is None:
            question = settings[channel]['QUESTION']
            options = ''
            for option in settings[channel]['OPTIONS']:
                options += '{0} {1}\n'.format(str(settings[channel]['OPTIONS'][option]).ljust(8), option.capitalize())
            message = '```Current statistics of {0}\n\n{1}```'.format(question, options)
            await self.bot.say(message)
        elif context.invoked_subcommand is None:
            await send_cmd_help(context)

    @vote.command(pass_context=True, no_pm=True)
    async def current(self, context):
        """Shows current poll results."""
        settings = fileIO(self.poll_data, "load")
        channel = context.message.channel.id
        if channel in settings:
            question = settings[channel]['QUESTION']
            options = ''
            for option in settings[channel]['OPTIONS']:
                options += '{} {}\n'.format(str(settings[channel]['OPTIONS'][option]).ljust(8), option.capitalize())
            message = '```Current statistics of {0}\n\n{1}```'.format(question, options)
        else:
            message = 'There\'s no poll active in this channel.'
        await self.bot.say(message)

    @vote.command(pass_context=True, no_pm=True)
    async def cast(self, context, *vote: str):
        vote = " ".join(vote)
        settings = fileIO(self.poll_data, "load")
        user_id = context.message.author.id
        user_name = context.message.author.name
        channel = context.message.channel.id
        if channel in settings:
            if user_id not in settings[channel]['VOTERS']:
                if vote.upper() in settings[channel]['OPTIONS']:
                    settings[channel]['OPTIONS'][vote.upper()] += 1
                    settings[channel]['VOTERS'] = user_id
                    fileIO(self.poll_data, "save", settings)
                    message = '{0} just voted *{1}*!'.format(user_name, vote)
            else:
                message = 'You\'ve already voted!'
        else:
            message = 'No poll active'
        await self.bot.say(message)

    @vote.command(pass_context=True, no_pm=True)
    async def start(self, context, *arguments: str):
        """poll start <question>;option;option;option (...)"""
        settings = fileIO(self.poll_data, "load")
        channel = context.message.channel.id
        starter = context.message.author.name
        if channel not in settings:
            poll = " ".join(arguments).split(';')
            question = poll[0]
            settings[channel] = {}
            settings[channel]['STARTER'] = starter
            settings[channel]['VOTERS'] = []
            settings[channel]['QUESTION'] = question
            settings[channel]['OPTIONS'] = {}
            for option in poll[1:]:
                settings[channel]['OPTIONS'][option.upper()] = 0
            message = '{0} started a poll with the question *{1}*'.format(starter, question)
            fileIO(self.poll_data, "save", settings)
        await self.bot.say(message)

    @vote.command(no_pm=True)
    async def old(self, *pid: str):
        """Retrieve an old poll with a given id."""
        settings = fileIO(self.poll_data, "load")
        if pid:
            pid = pid[0]
            if pid in settings:
                question = settings[pid]['QUESTION']
                options = ''
                for option in settings[pid]['OPTIONS']:
                    options += '{} {}\n'.format(str(settings[pid]['OPTIONS'][option]).ljust(8), option.capitalize())
                message = '```Statistics of {}(#{})\n\n{}```'.format(question, pid, options)
            else:
                message = 'Can\'t find poll with id #{}'.format(pid)
        await self.bot.say(message)

    @vote.command(pass_context=True, no_pm=True)
    async def stop(self, context):
        """Stops the poll. Only for the poll starter."""
        settings = fileIO(self.poll_data, "load")
        channel = context.message.channel.id
        starter = context.message.author.name
        manage_channels = context.message.author.permissions_in(context.message.channel).manage_channels
        if channel in settings:
            if settings[channel]['STARTER'] == starter:
                poll_id = str(int(time()))
                settings[poll_id] = settings[channel]
                del settings[channel]
                fileIO(self.poll_data, "save", settings)
                question = settings[poll_id]['QUESTION']
                options = ''
                for option in settings[poll_id]['OPTIONS']:
                    options += '{} {}\n'.format(str(settings[poll_id]['OPTIONS'][option]).ljust(8), option.capitalize())
                message = '```Statistics of {} (#{})\n\n{}```'.format(question, poll_id, options)
            elif manage_channels:
                poll_id = str(int(time()))
                settings[poll_id] = settings[channel]
                del settings[channel]
                fileIO(self.poll_data, "save", settings)
                options = ''
                for option in settings[poll_id]['OPTIONS']:
                    options += '{} {}\n'.format(str(settings[poll_id]['OPTIONS'][option]).ljust(8), option.capitalize())
                message = '```Statistics of {} (#{})\n\n{}```'.format(question, poll_id, options)
            else:
                message = 'You didn\'t start the poll.'

        else:
            message = 'There\'s no poll active in this channel.'
        await self.bot.say(message)


def check_folder():
    if not os.path.exists("data/vote"):
        print("Creating data/vote folder...")
        os.makedirs("data/vote")


def check_file():
    poll = {}
    f = "data/vote/vote.json"
    if not fileIO(f, "check"):
        print("Creating default vote.json...")
        fileIO(f, "save", poll)


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Vote(bot))
