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
		self.audio_player = False

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
		self.audio_player.stop()
		await voice_client.disconnect()

	async def listener(self, message):
		await asyncio.sleep(0.2)
		author = message.author
		server = message.server
		if not message.channel.is_private:
			mentioned = message.server.me.mentioned_in(message)
			if self.bot.user.id != author.id:
				if mentioned:
					if self.voice_connected(server) and not self.audio_player:
						await self.play_song(server)
						self.audio_player.start()
					elif self.audio_player:
						if not self.audio_player.is_playing():
							await self.play_song(server)
							self.audio_player.start()

	async def play_song(self, server):
		path = 'data/downloader/paddo-cogs/cat/data/sounds/'
		#path = 'data/sounds/'
		sound = [f for f in listdir(path) if isfile(join(path, f))]
		voice_client = self.voice_client(server)
		self.audio_player = voice_client.create_ffmpeg_player(path+random.choice(sound))


def setup(bot):
	n = Cat(bot)
	bot.add_listener(n.listener, 'on_message')
	bot.add_cog(n)
