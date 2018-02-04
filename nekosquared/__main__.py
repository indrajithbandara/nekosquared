"""
Application entry point.
"""
from nekosquared.engine import bot
from nekosquared.shared import config

cfg_file = config.get_config_data('discord.yaml')

bot.Bot(cfg_file()).run()
