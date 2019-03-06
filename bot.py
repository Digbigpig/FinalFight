from discord.ext import commands
from cogs.utils.models import base
import settings
import logging
import traceback


# Logger Configuration
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Bot-setup


bot = commands.Bot(command_prefix=settings.PREFIX,
                   description=settings.DESCRIPTION,
                   pm_help=None,
                   owner_id=settings.OWNER_ID,
                   )

# Generate database schema
base.Base.metadata.create_all(base.engine)

if __name__ == '__main__':

    # Attempt to load the extensions
    for ext in settings.EXTENSIONS:
            try:
                bot.load_extension(ext)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                print('Failed to load extension {}\n{}: {}'.format(ext, type(e).__name__, e))

    # Run the bot
    bot.run(settings.KEY)
