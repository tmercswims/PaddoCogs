import os
from discord.ext import commands
from .utils.dataIO import fileIO
from difflib import SequenceMatcher
import asyncio

class Games:
	def __init__(self, bot):
		self.bot = bot

	def match(self, a, b):
		return SequenceMatcher(None, a, b).ratio()

	async def listener(self, before, after):
		server = after.server
		filename = 'data/games/{}.json'.format(server.id)
		if not fileIO(filename, "check"):
			data = {}
			fileIO(filename, "save", data)
		else:
			data = fileIO(filename, "load")
		if not after.bot and after.game is not None:
			if before.game is None:
				before_game = ''
			else:
				before_game = before.game.name
			match = self.match(before_game, after.game.name)
			if match < 0.89 and len(after.game.name) > 2:
				game = [game for game in data if self.match(game.upper(), after.game.name.upper()) > 0.89]
				print(before_game, after.game.name, game, server.id)
				if game:
					data[game[0]] +=1
				else:
					data[after.game.name] = 1

			fileIO(filename, "save", data)

	@commands.command(pass_context=True, no_pm=True, name='games')
	async def _games(self, context):
		"""Shows top 10 most popular games on this server."""

		server = context.message.server
		filename = 'data/games/{}.json'.format(server.id)
		if fileIO(filename, "check"):
			data = fileIO(filename, "load")


			games_played = sorted(data, key=lambda x: data[x], reverse=True)
			message = '```Most popular games played on {}\n\n'.format(server.name)
			for i, game in enumerate(games_played, 1):
				if i > 10:
					break
				message+='{:<5}{:<10}\n'.format(i, game)
			message+='```'
			await self.bot.say(message)

def check_folder():
	if not os.path.exists('data/games'):
		print('Creating data/games folder...')
		os.makedirs('data/games')

def setup(bot):
	check_folder()
	n = Games(bot)
	bot.add_listener(n.listener, 'on_member_update')
	bot.add_cog(n)
