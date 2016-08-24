class Maolmao:
	def __init__(self, bot):
		self.bot = bot
		self.base = 'data/downloader/paddo-cogs/maolmao/data/maolmao.png'

	async def listener(self, message):
		if message.author.id != self.bot.user.id:
			if message.content.lower().startswith('ayy') or message.content.lower().startswith('aayy'):
				await self.bot.send_file(context.message.channel, self.base)

def setup(bot):
    n = Maolmao(bot)
    bot.add_listener(n.listener, "on_message")
    bot.add_cog(n)
