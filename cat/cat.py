from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks
import random
import asyncio
from os import listdir
from os.path import isfile, join

class Cat:
	def __init__(self, bot):
		self.bot = bot
		self.lock = False

	def voice_connected(self, server):
		if self.bot.is_voice_connected(server):
			return True
		return False

	def voice_client(self, server):
		return self.bot.voice_client_in(server)

	@commands.group(pass_context=True, no_pm=True, name='voice', aliases=['vc'])
	async def _vc(self, context):
		"""[join/leave]"""
		if context.invoked_subcommand is None:
			await send_cmd_help(context)

	@_vc.command(hidden=True, pass_context=True, no_pm=True, name='join', aliases=['connect'])
	@checks.serverowner_or_permissions()
	async def _join(self, ctx):
		"""Joins your voice channel"""
		author = ctx.message.author
		server = ctx.message.server
		channel = author.voice_channel
		if not self.voice_connected(server):
			await self.bot.join_voice_channel(channel)

	@_vc.command(hidden=True, pass_context=True, no_pm=True, name='leave', aliases=['disconnect'])
	@checks.serverowner_or_permissions()
	async def _leave(self, ctx):
		"""Leaves your voice channel"""
		server = ctx.message.server
		if not self.voice_connected(server):
			return
		voice_client = self.voice_client(server)
		await voice_client.disconnect()

	async def listener(self, message):
		await asyncio.sleep(0.8)
		author = message.author
		server = message.server
		content = message.content
		if self.bot.user.id != author.id:
			if self.bot.user.mention in content:
				if self.voice_connected(server) and not self.lock and author.voice_channel != None:
					path = 'data/downloader/paddo-cogs/cat/data/sounds'
					sound = [f for f in listdir(path) if isfile(join(path, f))]
					voice_client = self.voice_client(server)
					player = voice_client.create_ffmpeg_player(path+'/'+random.choice(sound))
					player.start()
					await self.bot.delete_message(message)
					while player.is_playing():
						self.lock = True
					self.lock = False

def setup(bot):
	n = Cat(bot)
	bot.add_listener(n.listener, 'on_message')
	bot.add_cog(n)
