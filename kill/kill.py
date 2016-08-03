from discord.ext import commands
import random
import discord

class Kill:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def kill(self, context, member : discord.Member):
        """Have you always wanted to kill someone? If so, do it in a creative way!"""
        killer = context.message.author.mention
        victim = member.mention
        ways_to_kill = {}
        ways_to_kill['0'] = '{0} screams in sheer terror and agony as a giant mutated creature with huge muscular arms grab {0}\'s head.'.format(victim)
        ways_to_kill['1'] = '{0} shoves a double barreled shotgun into {1}\'s mouth and squeezes the trigger of the gun, causing {1}\'s head to horrifically explode like a ripe pimple, splattering the young person\'s brain matter, gore, and bone fragments all over the walls and painting it a crimson red.'.format(killer, victim)
        ways_to_kill['3'] = 'Screaming in sheer terror and agony, {0} is horrifically dragged into the darkness by unseen forces, leaving nothing but bloody fingernails and a trail of scratch marks in the ground from which the young person had attempted to halt the dragging process.'.format(victim)
        ways_to_kill['4'] = '{0} takes a machette and starts hacking away on {1}, chopping {1} into dozens of pieces.'.format(killer, victim)
        ways_to_kill['5'] = '{0} pours acid over {1}. *"Well don\'t you look pretty right now?"*'.format(killer, victim)
        compile_kills = [ways_to_kill[i] for i in ways_to_kill]
        await self.bot.say('**{0}**'.format(random.choice(compile_kills)))

def setup(bot):
    n = Kill(bot)
    bot.add_cog(n)
