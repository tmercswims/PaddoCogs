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
			author = message.author
			channel = message.channel
			content = message.content
			timestamp = message.timestamp
			if server.id not in self.data:
				self.data[server.id] = {}
			if author.id not in self.data[server.id]:
				self.data[server.id][author.id] = {}
			if author.nick:
				self.data[server.id][author.id]['NAME'] = '{} ({})'.format(author.name, author.nick)
			else:
				self.data[server.id][author.id]['NAME'] = author.name
			self.data[server.id][author.id]['TIMESTAMP'] = str(timestamp)[:-7]
			self.data[server.id][author.id]['MESSAGE'] = content
			self.data[server.id][author.id]['CHANNEL'] = channel.mention

	@commands.command(pass_context=True, no_pm=True, name='seen', aliases=['s'])
	async def _seen(self, context, username: discord.Member):
		'''seen <@username>'''
		server = context.message.server
		author = username
		if server.id in self.data:
			if author.id in self.data[server.id]:
				timestamp = self.data[server.id][author.id]['TIMESTAMP']
				last_msg = self.data[server.id][author.id]['MESSAGE']
				user_name = self.data[server.id][author.id]['NAME']
				channel_name = self.data[server.id][author.id]['CHANNEL']
				message = '{} was last seen on `{} UTC` in {}, saying: {}'.format(user_name, timestamp, channel_name, last_msg)
			elif author.mention in self.data[server.id]:
				# legacy
				timestamp = self.data[server.id][author.mention]['TIMESTAMP']
				last_msg = self.data[server.id][author.mention]['MESSAGE']
				user_name = self.data[server.id][author.mention]['NAME']
				channel_name = self.data[server.id][author.mention]['CHANNEL']
				message = '{} was last seen on `{} UTC` in {}, saying: {}'.format(user_name, timestamp, channel_name, last_msg)
			else:
				message = 'I have not seen {} yet.'.format(author.name)
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
