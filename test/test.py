from discord.ext import commands


class Test:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def test(self):
        await self.bot.say('Test')


def setup(bot):
    n = Test(bot)
    bot.add_cog(n)
