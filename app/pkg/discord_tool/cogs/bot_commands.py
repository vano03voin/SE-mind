import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import has_guild_permissions, has_role
from app.pkg.restart_tools.tools import RestartManager


class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def echoo(self, ctx):
        """Повторяет сообщение за тобой"""

        #await ctx.message.delete()
        my_channel = self.bot.get_channel(1055454152668495913)
        await my_channel.send(ctx)

    @commands.check_any(has_guild_permissions(administrator=True), has_role('Hard Support'))
    @commands.command()
    async def restart_server(self, ctx):
        """Повторяет сообщение за тобой"""
        for server in self.bot.servers:
            if server.settings['commands_chat_id'] == str(ctx.channel.id):
                await ctx.send('Hard restart strart, i wish u turn on autostart on server...')
                server.turn_off()
                await asyncio.sleep(10)
                server.turn_on()
                break
        await ctx.send('U dont chose this chanel on any server...')


async def setup(bot):
    await bot.add_cog(Text(bot))
