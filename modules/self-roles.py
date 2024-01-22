from dataclasses import dataclass, asdict
import json
from interactions import *
from interactions.api.events import MessageReactionAdd, MessageReactionRemove
from utils.config import get_item
from utils.DictToDataclass import dict_to_dataclass
import re
    
class Command(Extension):
    
    async def get_role_data(self, guild_data: dict, message_id: int, guild_id: int, emoji):
        guild_data = self.get_selfrole_data(guild_id)
        
        role_id = 0
        self_roles = []
        role_name = ''
        
        if guild_data is None:
            return
        
        for data in guild_data['messages']:
            if data['message_id'] == message_id:
                self_roles = data['self_roles']
                
        if emoji.id is None:
            compare_emoji = emoji.name
        else:
            compare_emoji = emoji.id
                
        for role in self_roles:
            
            if compare_emoji == role['emoji']:
                role_id = role['id']
                role_name = role['name']
                    
        if not role_id:
            return None, None
        
        return role_id, role_name
    
    @listen(MessageReactionAdd)
    async def on_reaction_add(self, event: MessageReactionAdd):
        if event.author.bot:
            return
        
        if event.message.embeds[0].footer.text != 'Self Roles':
            return
        
        guild_data = self.get_selfrole_data(event.message.guild.id)
        
        role_id, role_name = await self.get_role_data(guild_data, event.message.id, event.message.guild.id, event.emoji)
        
        if role_id is None:
            return
        
        dm_channel = await event.author.user.fetch_dm()

        await event.author.add_role(role_id)
        await dm_channel.send(f'Successfully added the `{role_name}` role to you!\n\nSimply unreact to remove it.')
        
    @listen(MessageReactionRemove)
    async def on_reaction_remove(self, event: MessageReactionRemove):
        if event.author.bot:
            return
        
        if event.message.embeds[0].footer.text != 'Self Roles':
            return
        
        guild_data = self.get_selfrole_data(event.message.guild.id)
        
        role_id, role_name = await self.get_role_data(guild_data, event.message.id, event.message.guild.id, event.emoji)
        
        if role_id is None:
            return
        
        await event.author.remove_role(role_id)
        
            
    def update_selfrole_data(self, guild_id: int, data):
        # Use a context manager for file operations
        with open('data/selfroledata.json', 'r') as f:
            json_data = json.load(f)

        json_data[str(guild_id)] = data

        # Write the updated json_data back to the file
        with open('data/selfroledata.json', 'w') as f:
            json.dump(json_data, f, indent=2)
            
    def get_selfrole_data(self, guild_id: int):
        with open('data/selfroledata.json', 'r') as f:
            try:
                return json.load(f)[str(guild_id)]
            except:
                return {}
        
    def message_selfrole_validation(self, message: Message):
        if not message.author.bot:
            return False
        
        if len(message.embeds) == 0:
            return False
        
        embed = message.embeds[0]
        
        if embed.footer is None:
            return False
        
        if embed.footer.text != 'Self Role':
            return False
        
        return True
            
    @slash_command(description='Base Command for Self Roles')
    async def selfroles(self, ctx: SlashContext):
        return
    
    def get_field(self, index: int, name: str, emoji: [str | int], description: str):
        return EmbedField(
            name=f'{index}. {name}',
            value=f'{emoji} - *{description}*'
        )
        
    
    @selfroles.subcommand(sub_cmd_description='Create the self role embed message, which is automatically updated with your roles.')
    @slash_default_member_permission(Permissions.MANAGE_CHANNELS)
    @slash_option(name='channel', description='Channel to create the message in.', opt_type=OptionType.CHANNEL, required=True)
    @slash_option(name='title', description='The message title.', opt_type=OptionType.STRING, required=True)
    @slash_option(name='message', description='The message content.', opt_type=OptionType.STRING, required=True)
    @slash_option(name='color', description='The color of the embed. Use hex color codes.', opt_type=OptionType.STRING, required=False)
    async def create_message(self, ctx: SlashContext, channel: GuildText, title: str, message: str, color: str = ''):
        
        color = color.removeprefix('#')
        
        embed = Embed(
            title=title,
            description=message
        )
        
        if color:
            embed.color = int(color, 16)
            
        embed.set_footer('Self Role')

        msg = await channel.send(embed=embed)
        
        guild_data = self.get_selfrole_data(ctx.guild_id)
        
        if not guild_data:
            guild_data['messages'] = []
        
        guild_data['messages'].append({'index': len(guild_data['messages']), 'message_id': msg.id, 'channel_id': channel.id, 'self_roles': []})
        
        self.update_selfrole_data(ctx.guild_id, guild_data)
        
        await ctx.send(f'Successfully created message. Copy this ID, as you will need it to add roles or edit the message: ``{msg.id}``', ephemeral=True)
        
    @selfroles.subcommand(sub_cmd_description='Create the self role embed message, which is automatically updated with your roles.')
    @slash_default_member_permission(Permissions.MANAGE_CHANNELS)
    @slash_option(name='message_id', description='The ID of the message to edit.', opt_type=OptionType.STRING, required=True)
    @slash_option(name='title', description='The message title.', opt_type=OptionType.STRING, required=True)
    @slash_option(name='message', description='The message content.', opt_type=OptionType.STRING, required=True)
    @slash_option(name='color', description='The color of the embed. Use hex color codes.', opt_type=OptionType.STRING, required=False)
    async def edit_message(self, ctx: SlashContext, message_id: int, title: str, message: str, color: str = ''):
        
        color = color.removeprefix('#')
        
        data = self.get_selfrole_data(ctx.guild_id)
        
        message_id = int(message_id)
        
        if data is None:
            return await ctx.send('There are no messages to edit.', ephemeral=True)
        
        channel_id = 0
        
        self_roles = []
        
        for selfrole in data['messages']:        
            if selfrole['message_id'] == message_id:
                channel_id = selfrole['channel_id']
                self_roles = selfrole['self_roles']
                break
        else:
            return await ctx.send('There are no messages to edit.', ephemeral=True)
        
        channel: GuildText = ctx.guild.get_channel(channel_id)
        message_ = await channel.fetch_message(message_id)
        
        if not self.message_selfrole_validation(message_):
            return await ctx.send('This is not a valid selfrole message.', ephemeral=True)
        
        embed = Embed(
            title=title,
            description=message,
        )
        
        if color:
            embed.color = int(color, 16)
        else:
            embed.color = message_.embeds[0].color
            
        embed.set_footer('Self Role')
        
        embed.fields = []
        
        for i, role in enumerate(self_roles):
            
            if type(role['emoji']) == int:
                emoji = f'<:any:{role["emoji"]}>'
            else:
                emoji = role['emoji']
            
            embed.fields.append(self.get_field(i + 1, role['name'], emoji, role['description']))
        
        await message_.edit(embed=embed)
        
        await ctx.send('Message has been edited.', ephemeral=True)
        
    @selfroles.subcommand(sub_cmd_description='Add a role to the self role embed message.')
    @slash_default_member_permission(Permissions.MANAGE_ROLES)
    @slash_option(name='message_id', description='The ID of the message to edit.', opt_type=OptionType.STRING, required=True)
    @slash_option(name='role', description='The role to add.', opt_type=OptionType.ROLE, required=True)
    @slash_option(name='description', description='The description of the role.', opt_type=OptionType.STRING, required=True)
    @slash_option(name='emoji', description='The emoji to use for the role.', opt_type=OptionType.STRING, required=True)
    async def add_role(self, ctx: SlashContext, message_id: int, role: Role, emoji: str, description: str):
        
        guild_data = self.get_selfrole_data(ctx.guild_id)
        
        r_emoji = re.compile(r'<:([a-zA-Z0-9_]+):([0-9]+)>')
        match_ = r_emoji.match(emoji)
        
        if match_:
            emoji = int(match_.group(2))
        
        message_id = int(message_id)
        
        if guild_data is None:
            return await ctx.send('There are no messages to edit.', ephemeral=True)

        message_data = None
        
        for msg in guild_data['messages']:
            if msg['message_id'] == message_id:
                message_data = msg
                
                msg['self_roles'].append({'emoji': emoji, 'name': role.name, 'description': description, 'id': role.id})
                break
        else:
            return await ctx.send('There are no messages to edit.', ephemeral=True)
        
        channel: GuildText = ctx.guild.get_channel(message_data['channel_id'])
        message = await channel.fetch_message(message_id)
        
        if not self.message_selfrole_validation(message):
            return await ctx.send('This is not a valid selfrole message.', ephemeral=True)
        
        embed = message.embeds[0]
        
        if type(emoji) is int:
            emoji = f'<:any:{emoji}>'
        
        embed.fields.append(self.get_field(len(embed.fields) + 1, role.name, emoji, description))
        
        try:
            await message.add_reaction(emoji)
        except:
            return await ctx.send('This is an invalid emoji.', ephemeral=True)
        
        await message.edit(embed=embed)
        
        self.update_selfrole_data(ctx.guild_id, guild_data)
        
        await ctx.send('Role has been added.', ephemeral=True)
        
    @selfroles.subcommand(sub_cmd_description='Delete a self role.')
    @slash_default_member_permission(Permissions.MANAGE_ROLES)
    @slash_option(name='message_id', description='The ID of the message to edit.', opt_type=OptionType.STRING, required=True)
    @slash_option(name='role', description='The role to remove.', opt_type=OptionType.ROLE, required=True)
    async def remove_role(self, ctx: SlashContext, message_id: int, role: Role):
        
        guild_data = self.get_selfrole_data(ctx.guild_id)
        
        if guild_data is None:
            return await ctx.send('There are no messages to edit.', ephemeral=True)
        
        message_id = int(message_id)
        
        message_data = None
        
        for msg in guild_data['messages']:
            if msg['message_id'] == message_id:
                message_data = msg
                break
        else:
            return await ctx.send('There are no messages to edit.', ephemeral=True)
        
        channel: GuildText = ctx.guild.get_channel(message_data['channel_id'])
        message = await channel.fetch_message(message_id)
        
        if not self.message_selfrole_validation(message):
            return await ctx.send('This is not a valid selfrole message.', ephemeral=True)
        
        embed = message.embeds[0]
        
        embed.fields = []
        
        found_role = False
        
        for i, d_role in enumerate(message_data['self_roles']):
            if d_role['id'] == role.id:
                del message_data['self_roles'][i]
                
                found_role = True
                break
            
        if not found_role:
            return await ctx.send('Role not found.', ephemeral=True)
        
        await message.clear_all_reactions()
            
        for i, d_role in enumerate(message_data['self_roles']):
            
            if type(d_role['emoji']) == int:
                emoji = f'<:any:{d_role["emoji"]}>'
                p_emoji = PartialEmoji(id=d_role['emoji'])
            else:
                emoji = d_role['emoji']
                p_emoji = d_role['emoji']
            
            embed.fields.append(self.get_field(i + 1, d_role['name'], emoji, d_role['description']))

            await message.add_reaction(p_emoji)
            
        guild_data['messages'][message_data['index']] = message_data
        
        self.update_selfrole_data(ctx.guild_id, guild_data)
        
        await message.edit(embed=embed)
        
        await ctx.send('Role has been removed.', ephemeral=True)
        
    @selfroles.subcommand(sub_cmd_description='Update a self role message.')
    @slash_default_member_permission(Permissions.MANAGE_ROLES)
    @slash_option(name='message_id', description='The ID of the message to edit.', opt_type=OptionType.STRING, required=True)
    async def update_message(self, ctx: SlashContext, message_id: int):
        
        guild_data = self.get_selfrole_data(ctx.guild_id)
        
        if guild_data is None:
            return await ctx.send('There are no messages to edit.', ephemeral=True)
        
        message_id = int(message_id)
        
        message_data = None
        
        for msg in guild_data['messages']:
            if msg['message_id'] == message_id:
                message_data = msg
                break
        else:
            return await ctx.send('There are no messages to edit.', ephemeral=True)
        
        channel: GuildText = ctx.guild.get_channel(message_data['channel_id'])
        message = await channel.fetch_message(message_id)
        
        if not self.message_selfrole_validation(message):
            return await ctx.send('This is not a valid selfrole message.', ephemeral=True)
        
        embed = message.embeds[0]
        
        embed.fields = []
        
        await message.clear_all_reactions()
        
        for i, role in enumerate(message_data['self_roles']):
            
            if type(role['emoji']) == int:
                emoji = f'<:any:{role["emoji"]}>'
                p_emoji = PartialEmoji(id=role['emoji'])
            else:
                emoji = role['emoji']
                p_emoji = role['emoji']
            
            embed.fields.append(self.get_field(i + 1, role['name'], emoji, role['description']))

            await message.add_reaction(p_emoji)
        
        self.update_selfrole_data(ctx.guild_id, guild_data)
        
        await message.edit(embed=embed)
        
        await ctx.send('Message has been updated.', ephemeral=True)