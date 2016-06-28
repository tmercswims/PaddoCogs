from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks
import random
from os import listdir
from os.path import isfile, join

class Animalsounds:
	def __init__(self, bot):
		self.bot = bot
		self.audio_player = False
		#self.sound_base = 'data/downloader/paddo-cogs/cat/data/sounds'
		self.sound_base = 'data/sounds/'

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
	async def _join(self, context):
		"""Joins your voice channel"""
		author = context.message.author
		server = context.message.server
		channel = author.voice_channel
		if not self.voice_connected(server):
			await self.bot.join_voice_channel(channel)

	@_vc.command(hidden=True, pass_context=True, no_pm=True, name='leave', aliases=['disconnect'])
	@checks.serverowner_or_permissions()
	async def _leave(self, context):
		"""Leaves your voice channel"""
		server = context.message.server
		if not self.voice_connected(server):
			return
		voice_client = self.voice_client(server)

		if self.audio_player:
			self.audio_player.stop()
		await voice_client.disconnect()

	@commands.command(no_pm=True, pass_context=True, name='meow', aliases=['cat'])
	async def _meow(self, context):
		animal = 'cat'
		server = context.message.server
		if not context.message.channel.is_private:
			if self.voice_connected(server) and not self.audio_player:
				await self.play_song(server, '{}/{}'.format(self.path, animal))
				self.audio_player.start()
			elif self.audio_player:
				if not self.audio_player.is_playing():
					await self.play_song(server, '{}/{}/'.format(self.path, animal))
					self.audio_player.start()

	@commands.command(no_pm=True, pass_context=True, name='bark', aliases=['dog'])
	async def _bark(self, context):
		animal = 'dog'
		server = context.message.server
		if not context.message.channel.is_private:
			if self.voice_connected(server) and not self.audio_player:
				await self.play_song(server, '{}/{}'.format(self.path, animal))
				self.audio_player.start()
			elif self.audio_player:
				if not self.audio_player.is_playing():
					await self.play_song(server, '{}/{}/'.format(self.path, animal))
					self.audio_player.start()

	@commands.command(no_pm=True, name='chatter', aliases=['magpie'])
	async def _chatter(self):
		print('magpie')
		pass

	@commands.command(no_pm=True, name='croak', aliases=['frog'])
	async def _croak(self):
		pass

	@commands.command(no_pm=True, name='neigh', aliases=['horse'])
	async def _neigh(self):
		pass

	@commands.command(no_pm=True, name='moo', aliases=['cow'])
	async def _moo(self):
		pass

	@commands.command(no_pm=True, name='trumpet', aliases=['elephant'])
	async def _trumpet(self):
		pass

	@commands.command(no_pm=True, name='quack', aliases=['duck'])
	async def _quack(self):
		pass

	@commands.command(no_pm=True, name='honk', aliases=['goose'])
	async def _honk(self):
		pass

	@commands.command(no_pm=True, name='oink', aliases=['pig'])
	async def _oink(self):
		pass

	@commands.command(no_pm=True, name='hoot', aliases=['owl'])
	async def _hoot(self):
		pass

	@commands.command(no_pm=True, name='sing', aliases=['whale'])
	async def _whale(self):
		pass

	async def play_song(self, server, path):
		sound = [f for f in listdir(path) if isfile(join(path, f))]
		voice_client = self.voice_client(server)
		self.audio_player = voice_client.create_ffmpeg_player(path+random.choice(sound))

def setup(bot):
	n = Animalsounds(bot)
	bot.add_cog(n)
