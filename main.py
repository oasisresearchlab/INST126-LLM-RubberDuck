from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Thread
from response import get_response

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

# Dictionary to store thread IDs and their associated user and context
bot_created_threads = {}

# Function to split messages into chunks of 2000 characters or fewer
def split_message(message: str) -> list:
    return [message[i:i+2000] for i in range(0, len(message), 2000)]

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    try:
        async with message.channel.typing():
            # Collect the last 10 messages for context
            messages = []
            async for msg in message.channel.history(limit=10):
                messages.append(msg)
            messages.reverse()  # Reverse to maintain chronological order

            context = "\n".join([f"{msg.author.display_name}: {msg.content}" for msg in messages])
            full_message = f"{context}\n\n{message.author.display_name}: {user_message}"

            response: str = get_response(full_message)
            response_chunks = split_message(response)
            
            if isinstance(message.channel, Thread):
                # If the message is in a thread created by the bot, respond in the thread
                if message.channel.id in bot_created_threads:
                    for chunk in response_chunks:
                        await message.channel.send(chunk)
            else:
                if message.guild:
                    # Clean up the user message to remove the bot mention
                    cleaned_message = user_message.replace(f'<@{client.user.id}>', '').strip()
                    # Create a thread for the response if it's in a guild
                    thread_name = (cleaned_message[:90] + '...') if len(cleaned_message) > 90 else cleaned_message
                    thread = await message.create_thread(name=f"{message.author.display_name}: {thread_name}", auto_archive_duration=60)
                    bot_created_threads[thread.id] = {'user_id': message.author.id, 'context': context}
                    for chunk in response_chunks:
                        await thread.send(chunk)
                else:
                    # Respond directly in DMs
                    for chunk in response_chunks:
                        await message.channel.send(chunk)
    except Exception as e:
        print(e)

# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    user_message: str = message.content

    # Handle the !about command
    if user_message.startswith('!about'):
        about_message = (
            "Hello! I'm a Python bot here to assist you with Python questions. "
            "Feel free to ask me anything about Python programming. "
        )
        await message.channel.send(about_message)
        return

    if isinstance(message.channel, Thread) and message.channel.id in bot_created_threads:
        # If the message is in a thread created by the bot
        username: str = str(message.author)
        channel: str = str(message.channel)

        print(f'[Thread {channel}] {username}: "{user_message}"')
        await send_message(message, user_message)
    elif message.guild is None or client.user.mentioned_in(message):
        # If the bot is mentioned in a guild or if it's a direct message
        username: str = str(message.author)
        channel: str = str(message.channel)

        print(f'[{channel}] {username}: "{user_message}"')
        await send_message(message, user_message)

# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()
