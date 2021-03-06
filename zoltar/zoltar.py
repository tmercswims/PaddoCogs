from discord.ext import commands
import random


class Zoltar:
    def __init__(self, bot):
        self.bot = bot
        with open('data/zoltar/fortunes.txt', encoding='utf-8', mode="r") as f:
            self._fortunes = f.read().split('\n')

    @commands.command(name='zoltar')
    async def _zoltar(self):
        message = random.choice(self._fortunes)
        await self.bot.say('_{}_\n\n_Your Lucky Numbers: **{}, {}, {}, {}, {}, {}**_'.format(message, random.randint(1, 100), random.randint(1, 100), random.randint(1, 100), random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)))


def setup(bot):
    n = Zoltar(bot)
    bot.add_cog(n)
