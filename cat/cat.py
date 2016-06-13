from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks
import random

class Catsounds:
	def __init__(self, bot):
		self.bot = bot

	def voice_connected(self, server):
		if self.bot.is_voice_connected(server):
			return True
		return False

	def voice_client(self, server):
		return self.bot.voice_client_in(server)

	@commands.group(pass_context=True, no_pm=True, name='voice', aliases=['vc'])
	async def _vc(self, context):
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
		server = ctx.message.server
		if not self.voice_connected(server):
			return
		voice_client = self.voice_client(server)
		await voice_client.disconnect()

	async def listener(self, message):
		sound = ['meow_1.mp3', 'meow_2.mp3', 'meow_3.mp3', 'meow_4.mp3', 'meow_7.mp3', 'meow_8.mp3', 'meow_9.mp3', 'meow_10.mp3', 'meow_11.mp3', 'meow_12.mp3', 'meow_13.mp3', 'meow_14.mp3', 'meow_15.mp3', 'meow_16.mp3']
		author = message.author
		server = message.server
		content = message.content
		if self.bot.user.id != author.id:
			if self.bot.user.mention in content:
				if self.voice_connected(server):
					voice_client = self.voice_client(server)
					player = voice_client.create_ffmpeg_player('data/downloader/paddo-cogs/cat/data/sounds/'+random.choice(sound))
					player.start()


def setup(bot):
	n = Catsounds(bot)
	bot.add_listener(n.listener, 'on_message')
	bot.add_cog(n)
