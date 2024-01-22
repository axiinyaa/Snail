from interactions import *
from interactions.api.events import MessageCreate, MessageReactionAdd
import regex

class Snaft(Extension):
    @listen()
    async def snaft(self, event: MessageCreate):
        if event.message.author.bot:
            return
        
        if not event.message.channel.id == 634462914136375307:
            return
        
        await self.judgement(event.message.content.lower(), event.message)
            
    async def judgement(self, content: str, message):
        
        content = content.replace(' ', '')
        
        if 'snaft' not in content:
            return False
        
        print('do it')
        
        if content == 'snaft':
            await message.add_reaction('✅')
        else:
            await message.add_reaction('❌')
            
        return True
            
    @listen()
    async def on_reaction(self, event: MessageReactionAdd):
        if event.author.bot:
            return
        
        if not event.message.channel.id == 634462914136375307:
            return
        
        if 'snaft' not in event.message.content.lower():
            return
        
        await self.judgement(event.message.content.lower(), event.message)
        
        await event.message.clear_all_reactions()
