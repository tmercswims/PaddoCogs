from discord.ext import commands
from .utils.dataIO import fileIO
import asyncio
import discord
import os

class Seen:
	'''Check when someone was last seen.'''
	def __init__(self, bot):
		self.bot = bot
		self.seen_path = 'data/seen/seen.json'
		self.data = fileIO(self.seen_path, 'load')

	async def listener(self, message):
		if not message.channel.is_private and self.bot.user.id != message.author.id:
		server = message.server
		channel = message.channel
		author = message.author
		timestamp = message.timestamp
		filename = 'data/seen/{}/{}.json'.format(server.id, author.id)
		if not os.path.exists('data/seen/{}'.format(server.id)):
			os.makedirs('data/seen/{}'.format(server.id))
		if not fileIO(filename, 'check'):
			data = {}
			data['TIMESTAMP'] = str(timestamp)[:-7]
			data['MESSAGE'] = message.content
			data['CHANNEL'] = channel.mention
			fileIO(filename, 'save', data)
		else:
			data = fileIO(file_name, 'load')
			data['TIMESTAMP'] = str(timestamp)[:-7]
			data['MESSAGE'] = message.content
			data['CHANNEL'] = channel.mention
			fileIO(filename, 'save', data)

	@commands.command(pass_context=True, no_pm=True, name='seen', aliases=['s'])
	async def _seen(self, context, username: discord.Member):
		'''seen <@username>'''
		server = context.message.server
		author = username
		if server.id in self.data:
			if author.id in self.data[server.id]:
				timestamp = self.data[server.id][author.id]
				message = '{} was last seen on `{} UTC`'.format(author.display_name, timestamp)
			else:
				message = 'I have not seen {} yet.'.format(author.display_name)
		else:
			message = 'I haven\'t seen anyone in this server yet!'
		await self.bot.say('{}'.format(message))

	async def _store_data(self):
		await self.bot.wait_until_ready()
		while self is self.bot.get_cog('Seen'):
			fileIO(self.seen_path, 'save', self.data)
			await asyncio.sleep(60)

def check_folder():
	if not os.path.exists('data/seen'):
		print('Creating data/seen folder...')
		os.makedirs('data/seen')

def check_file():
	data = {}
	f = 'data/seen/seen.json'
	if not fileIO(f, 'check'):
		print('Creating default seen.json...')
		fileIO(f, 'save', data)

def setup(bot):
	check_folder()
	check_file()
	n = Seen(bot)
	bot.add_listener(n.listener, 'on_message')
	bot.loop.create_task(n._store_data())
	bot.add_cog(n)
