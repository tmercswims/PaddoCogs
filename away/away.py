from discord.ext import commands
from cogs.utils.dataIO import dataIO
import os


class Away:
    """Le away cog"""
    def __init__(self, bot):
        self.bot = bot
        self.away_data = 'data/away/away.json'

    async def listener(self, message):
        tmp = {}
        for mention in message.mentions:
            tmp[mention] = True
        if message.author.id != self.bot.user.id:
            data = dataIO.load_json(self.away_data)
            for mention in tmp:
                if mention.mention in data:
                    if data[mention.mention]['MESSAGE'] is None:
                        msg = '{} is currently away.'.format(mention.name)
                    else:
                        msg = '{} is currently away and has set a personal message: {}'.format(mention.name, data[mention.mention]['MESSAGE'])
                    await self.bot.send_message(message.channel, msg)

    @commands.command(pass_context=True, name="away")
    async def _away(self, context, *message: str):
        """Tell the bot you're away or back."""
        data = dataIO.load_json(self.away_data)
        author_mention = context.message.author.mention
        if author_mention in data:
            del data[author_mention]
            msg = 'You\'re now back.'
        else:
            data[context.message.author.mention] = {}
            if 0 < len(message) < 256:
                data[context.message.author.mention]['MESSAGE'] = " ".join(context.message.clean_content.split()[1:])
            else:
                data[context.message.author.mention]['MESSAGE'] = None
            msg = 'You\'re now set as away.'
        dataIO.save_json(self.away_data, data)
        await self.bot.reply(msg)


def check_folder():
    if not os.path.exists('data/away'):
        print('Creating data/away folder...')
        os.makedirs('data/away')


def check_file():
    away = {}
    f = 'data/away/away.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, away)
        print('Creating default away.json...')


def setup(bot):
    check_folder()
    check_file()
    n = Away(bot)
    bot.add_listener(n.listener, 'on_message')
    bot.add_cog(n)
