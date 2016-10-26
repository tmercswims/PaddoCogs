class Redlink:
    def __init__(self, bot):
        self.bot = bot

    async def listener(self, message):
        if message.author.id != self.bot.user.id:
            if '+/r/' in message.content.lower():
                msg = ''
                for x in message.content.split(" "):
                    if x.startswith('+/r/'):
                        msg += 'https://www.reddit.com{0}\n'.format(x[1:])
                await self.bot.send_message(message.channel, msg)


def setup(bot):
    n = Redlink(bot)
    bot.add_listener(n.listener, "on_message")
    bot.add_cog(n)
