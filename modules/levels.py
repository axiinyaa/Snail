import random
from interactions import *
from interactions.api.events import MessageCreate
from utils.config import get_roles, get_item
from database import Levels, grab_mee6_levels_teehee

from datetime import datetime, timedelta

class Command(Extension):

    '''@slash_command()
    async def convert_mee6_levels(self, ctx: SlashContext):
        
        await ctx.send('Grabbing Mee6 Levels...')
        
        await grab_mee6_levels_teehee()'''
    
    @slash_command()
    @slash_option(
        'user',
        'Check the rank of another user.',
        OptionType.USER,
        required=True
    )
    async def rank(self, ctx: SlashContext, user: User):
        '''View your current rank, and the XP needed to get to the next level.'''
        
        await ctx.defer()
        
        # Bar Parameters
        bar_empty = '░'
        bar_filled = '█'
        
        bar_length = 15
        
        # Getting Level information
        player: Levels = await Levels(user.id, str(ctx.guild_id)).fetch()

        xp_needed = player.calculate_xp_needed(player.level)
        
        current_xp = player.current_xp
        
        #cereal has 26000k xp
        
        current_progress = round((current_xp / xp_needed) * bar_length)
        
        progress_bar = ''
        
        for bar in range(bar_length):
            if bar < current_progress:
                progress_bar += bar_filled
                continue
            
            progress_bar += bar_empty
            
        embed = Embed(description=f'**{current_xp:,} / {xp_needed:,} XP** - **Level {player.level}**\n{progress_bar}', color=0xf7a3e7)
        embed.set_author(name=f'{user.display_name}\'s current rank:', icon_url=user.display_avatar.url)
        
        await ctx.send(embed=embed)
        
    message_pool = {}
        
    @listen()
    async def snaft(self, event: MessageCreate):
        
        author = event.message.author
        
        if author.bot:
            return
        
        time = self.message_pool.get(author.id, None)
        user: Levels = await Levels(author.id, str(event.message.guild.id)).fetch()
        
        if time is not None:
            if datetime.now() < time:
                return
        
        levelled_up = await user.add_xp(random.randrange(15, 30))
        
        if levelled_up:
            
            embed = Embed(description=f'Congrats! {author.mention} levelled up to **Level {user.level}**!', color=0xf7a3e7)
            embed.set_author(name='Level Up!', icon_url=author.display_avatar.url)
            
            level_up_channel = get_item('level_up_channel', int(event.message.guild.id))
            
            if level_up_channel is not None:
                channel = await event.message.guild.fetch_channel(level_up_channel)
            else:
                channel = event.message.channel
            
            await channel.send(embed=embed)
            
        roles: dict[str, str] = get_roles('role-rewards', int(event.message.guild.id))
            
        if roles is not None:
        
            for level, role in roles.items():
                if author.has_role(role):
                    continue
                
                if user.level + 1 > int(level):
                    await author.add_role(role)
        
        self.message_pool[author.id] = datetime.now() + timedelta(minutes=1)