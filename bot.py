import logging
import traceback
from cogs.utils.models.base import Session
from discord.ext import commands
from discord.ext.commands import HelpFormatter

import settings

from cogs.utils.tests.inserts import rebuild_db

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
session = Session()

from cogs.utils.models import base
from cogs.utils.models.channel import Channel
from cogs.utils.models.hiscores_report import HiscoresReport
from cogs.utils.models.item import Item
from cogs.utils.models.item_inventory import ItemInventory
from cogs.utils.models.match import Match
from cogs.utils.models.player import Player
from cogs.utils.models.role import Role
from cogs.utils.models.server import Server
from cogs.utils.models.user import User

base.Base.metadata.create_all(base.engine)
session.commit()

if __name__ == '__main__':

    # Attempt to load the extensions
    for ext in settings.EXTENSIONS:
        try:
            bot.load_extension(ext)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
            print('Failed to load extension {}\n{}: {}'.format(ext, type(e).__name__, e))

    bot.run(settings.KEY)
