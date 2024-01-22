import os
import interactions

files = [f for f in os.listdir('modules') if f != '__pycache__']
commands = [f.replace('.py', '') for f in files]


def load_commands(client: interactions.Client):

    # Load each command using the client.load method
    [client.load_extension(f"modules.{command}") for command in commands]

    print(f"Loaded {len(commands)} modules.")