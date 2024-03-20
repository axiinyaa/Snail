from interactions import *

class Command(Extension):
    
    @slash_command(description='Pings the bot.')
    async def ping(self, ctx: SlashContext):
        await ctx.send(f'Pong! `{round(self.bot.latency * 1000)}ms`')