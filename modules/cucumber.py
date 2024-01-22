from interactions import *

class Cucumber(Extension):
    @slash_command(name='cucumber', description='Cucumber')
    async def cucumber(self, ctx: SlashContext):
        await ctx.send('https://cdn.discordapp.com/attachments/1181692967984046100/1191457105027272714/snail-cucumber-258532276.gif')