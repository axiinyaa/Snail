from interactions import *
from interactions.api.events import Startup, MessageCreate
from utils.config import get_item
from load_commands import load_commands
from database import create_connection
import re

print('Starting Bot...\n')

bot = Client(
    token=get_item('token'),
    intents=Intents.ALL,
)

load_commands(bot)

@listen(Startup)
async def on_startup(event: Startup):
    
    create_connection()
    
    print(f'{bot.user.username} is online!')
    
@listen()
async def snaft(event: MessageCreate):
    
    discord_regex = re.search(r'(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.+[a-z]', event.message.content)
    
    user = event.message.author
    
    if discord_regex is not None:
        joined_timestamp = user.joined_at
        message_timestamp = event.message.timestamp
        
        # Calculate the time difference in minutes
        time_delta = (message_timestamp - joined_timestamp).total_seconds() / 60

        # Ban if link was sent within a customizable time window (e.g., 10 minutes)
        if time_delta <= 10:
            await user.ban(reason='Spam Bot.', delete_message_seconds=100)
            
            with open('ban_hammer.txt', 'r') as f:
                amount = int(f.read())
            
            amount += 1
            
            with open('ban_hammer.txt', 'w') as f:
                f.write(str(amount))
            
            await event.message.channel.send(
                embed=Embed(
                    'get owned',
                    f'Successfully banned **{amount}** spam bots so far.',
                    color=0xf7a3e7
                )
            )
    
bot.start()