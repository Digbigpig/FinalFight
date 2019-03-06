import discord
import settings
from cogs.utils import querys, inserts


class Event:
    """
    Handles Discord Events.
    """

    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print('Logged in as:')
        print('Username: ' + self.bot.user.name)
        print('ID: ' + self.bot.user.id)
        print(f'Connected to {str(len(self.bot.servers))} servers | {str(len(set(self.bot.get_all_members())))} users.')
        print('------')

    async def on_server_join(self, server):
        # If the server is not in the database, add them to the database.

        if not querys.server_exists(server.id):
            print(f"Adding Server {server.name} to database.")
            inserts.create_server(server.id, server.name)
        else:
            print(f'Server {server.name} already in database.')

        emb = discord.Embed(title=f"Server {server.name} has joined the fight!",
                            type="rich",
                            description=f"{server.member_count} fighters strong!")
        emb.set_image(url=server.icon_url)

        await self.bot.send_message(destination=discord.Object(id=settings.BROADCAST_ID), embed=emb)

    async def on_server_remove(self, server):
        emb = discord.Embed(title=f"Server {server.name} has left the fight!",
                            type="rich", )
        emb.set_image(url=server.icon_url)

        await self.bot.send_message(destination=discord.Object(id=settings.BROADCAST_ID), embed=emb)


def setup(bot):
    bot.add_cog(Event(bot))
