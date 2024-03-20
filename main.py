from interactions import *
from interactions.api.events import Startup
from utils.config import get_item
from load_commands import load_commands
from database import create_connection

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
    
bot.start()