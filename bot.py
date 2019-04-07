import logging
import traceback

from discord.ext import commands
from discord.ext.commands import HelpFormatter

import settings
from cogs.utils.models import base

# Logger Configuration
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix=settings.PREFIX,
                   description=settings.DESCRIPTION,
                   pm_help=None,
                   owner_id=settings.OWNER_ID,
                   formatter=HelpFormatter(show_check_failure=True)
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

    bot.run(settings.KEY)
