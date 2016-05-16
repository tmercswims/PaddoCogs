from discord.ext import commands


class Crony:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def hue(self):
        await self.bot.say('Test')


def setup(bot):
    n = Cront(bot)
    bot.add_cog(n)
