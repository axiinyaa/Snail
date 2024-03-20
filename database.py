from dataclasses import asdict, dataclass, field
import json
from typing import Union, Dict, List
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from interactions import Snowflake, Extension, listen
from interactions.api.events import Startup
import requests
from utils.config import get_item
from datetime import datetime

# Define the Database Schema for The World Machine:
@dataclass
class Collection:
    _id: str
    _guild_id: str
        
    async def update(self, **kwargs):
        '''
        Update the current collection with the given kwargs.
        '''
        
        updated_data = await update_in_database(self, **kwargs)
        
        for k, v in asdict(updated_data).items():
            setattr(self, k, v)
        
    async def fetch(self):
        '''
        Fetch the current collection using id.
        '''
        
        self._id = str(self._id) # Make sure _id is string.
        
        return await fetch_from_database(self)
        
@dataclass
class Levels(Collection):
    total_xp: int = 0
    current_xp: int = 0
    level: int = 0
    
    def calculate_xp_needed(self, level: int = level):
        calc = 5 * (level ** 2) + (50 * level) + 100
        
        return calc
    
    async def add_xp(self, amount: int):
        xp_needed = self.calculate_xp_needed(self.level)
        
        levelled_up = False
        
        current_xp = self.current_xp + amount
        total_xp = self.total_xp + amount
        level = self.level
        
        while current_xp >= xp_needed:
            current_xp = current_xp - xp_needed
            level += 1
            
            xp_needed = self.calculate_xp_needed(level)
            
            levelled_up = True
        
        await self.update(current_xp=current_xp, total_xp=total_xp, level=level)
        
        return levelled_up
    


# ----------------------------------------------------

connection_uri = get_item('database')

connection = None

def create_connection():
    
    global connection
    
    if connection is not None:
        return
    
    connection = AsyncIOMotorClient(connection_uri, server_api=ServerApi('1'))

def get_database():
    
    if connection is None:
        create_connection()
        
    return connection.get_database('Snail')

async def fetch_from_database(collection: Collection) -> Collection:
        
    db = get_database()
    
    result = await db.get_collection(collection._guild_id).find_one({'_id': collection._id})
    
    if result is None:
        await new_entry(collection)
        return await fetch_from_database(collection)
    
    return collection.__class__(**result)

async def new_entry(collection: Collection):
    
    db = get_database()
    
    await db.get_collection(collection._guild_id).update_one({'_id': collection._id}, {'$set': asdict(collection)}, upsert=True)

async def update_in_database(collection: Collection, **kwargs):
    db = get_database()
    
    # Fetch the existing document from the database
    existing_data = asdict(collection)
    
    # Update only the specified fields in the existing document
    updated_data = {**existing_data, **kwargs}
    
    # Update the document in the database
    await db.get_collection(collection._guild_id).update_one({'_id': collection._id}, {'$set': updated_data}, upsert=True)
    
    # Create and return an updated instance of the collection
    updated_instance = collection.__class__(**updated_data)

    return updated_instance

async def fetch_mee6_levels(api, limit=1000, offset=0):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api}?limit={limit}") as response:
            result = await response.json()

    if not result:
        raise ValueError('Unable to get Mee6 API bwomp bwomp 👎👎👎👎👎')

    return result['players']

async def grab_mee6_levels_teehee():
    api = 'https://mee6.xyz/api/plugins/levels/leaderboard/158964992756940800'
    limit = 1000
    offset = 0

    try:
        while True:
            players = await fetch_mee6_levels(api, limit=limit)

            if not players:
                break  # No more players, exit the loop

            for i, player in enumerate(players):
                
                level = player['level']
                current_xp = player['detailed_xp'][0]
                total_xp = player['detailed_xp'][2]
                
                try:
                    await Levels(_id=player['id'], _guild_id="158964992756940800", total_xp=total_xp, current_xp=current_xp, level=level).fetch()
                    print(f'{i + offset}. Successfully added {player["id"]} to the database.')
                except Exception as e:
                    print(f'{i + offset}. Failed to add {player["id"]} to the database. ❌')
                    print(f'Error: {e}')

    except Exception as e:
        print(f'Error fetching Mee6 levels: {e}')