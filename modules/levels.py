import random
from interactions import *
from interactions.api.events import MessageCreate
from utils.config import get_roles, get_item
from database import Levels, get_database
import re

from datetime import datetime, timedelta

class LevelModule(Extension):

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
        
    def get_buttons(self, page: int):
        return [
            Button(
                style=ButtonStyle.RED,
                label='<',
                custom_id=f'move_page_-1_{page}'
            ),
            Button(
                style=ButtonStyle.RED,
                label='>',
                custom_id=f'move_page_1_{page}'
            ),
        ]
        
    @slash_command()
    async def leaderboard(self, ctx: SlashContext):
        
        await ctx.defer()
        
        documents = await self.get_levelling_data(str(ctx.guild_id))
        
        embed = await self.levelling_embed(ctx.author_id, 0, documents)
        
        await ctx.send(embed=embed, components=self.get_buttons(page=0))
            
    async def get_levelling_data(self, guild_id: str):
        
        database = get_database()
        collection = database.get_collection(guild_id)
        
        cursor = collection.find().sort({'total_xp': -1})
        
        return await cursor.to_list(length=100)
            
    async def levelling_embed(self, uid: int, page: int, levelling_data: list):
        
        start_index = page * 10  # Calculate the starting index for the subset
        end_index = (page + 1) * 10  # Calculate the ending index for the subset
        
        documents = levelling_data[start_index:end_index]
        
        result = '```ansi\n'
        
        is_in_top_100 = -1
        
        for i, document in enumerate(documents):
            user_level_data = Levels(**document)
            user: User = await self.bot.fetch_user(user_level_data._id)
            
            if user.id == uid:
                is_in_top_100 = i + start_index
            
            result += f'{(i + start_index) + 1}. [2;31m[1;31m[1;31m{user.display_name} [1;37m[1;37m[1;37m[1;37m[1;37m- [1;34m[4;34m[4;34m[4;35m{user_level_data.total_xp:,} XP[0m[4;34m[0m[4;34m[0m[1;34m[1;34m[0m[1;34m[0m[1;37m[0m[1;37m[0m[1;37m[0m[1;37m[0m[1;37m[0m[1;31m[0;31m[0;37m[0m[0;31m[0m[1;31m[0m[1;31m[0m[2;31m[0m\n'
        
        result += f'```'
        
        return Embed(
            'Leaderboard',
            description=result
        )
            
    page_pattern = re.compile(r'move_page_(.*)_(.*)')
    @component_callback(page_pattern)
    async def move_page(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        match_ = self.page_pattern.match(ctx.custom_id)
        
        if not match_:
            return
        
        direction = int(match_.group(1))
        page = int(match_.group(2))
        
        documents = await self.get_levelling_data(str(ctx.guild_id))
        
        if (page == 0 and direction == -1) or (page == 9 and (direction == 1 or len(documents) < 9)):
            return
        
        embed = await self.levelling_embed(ctx.author_id, page + direction, documents)
        
        await ctx.edit_origin(embed=embed, components=self.get_buttons(page=page + direction))
        
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
                
                if user.level > int(level):
                    await author.add_role(role)
        
        self.message_pool[author.id] = datetime.now() + timedelta(minutes=1)