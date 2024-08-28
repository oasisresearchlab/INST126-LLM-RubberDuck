from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Thread
from response import get_response
import requests
from PIL import Image
from io import BytesIO
from logs import log_to_google_sheets
import random
from datetime import datetime
import string
from logs import log_to_csv
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

def generate_unique_id():
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=6))
    unique_id = letters + numbers
    
    return unique_id

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_image_from_url(image_url: str) -> Image.Image:
    # Download the image from the URL
    response = requests.get(image_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Convert the image data into an Image object
        image = Image.open(BytesIO(response.content))
        return image
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")

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

            msg_images = [attachment.url for attachment in message.attachments if attachment.content_type.startswith('image/')]
            if len(msg_images)>1:
                await message.channel.send("You've given me too many images, Please give me one at a time.")
                return
            image=None
            if len(msg_images)==1:
                try:
                    image=get_image_from_url(msg_images[0])
                except Exception as e:
                    print("An exception occured when trying to fetch the attachment",e)
                    await message.channel.send("I couldn't fetch the image. Please try again.")
                    return
            response: str = get_response(full_message,image)

            
            message_type="Thread" if message.guild else "Direct Message"
            threadId=message.channel.id if message_type=="Thread" else ""
            userId=message.author.id
            messageId=message.id

            #Log the data in google sheets
            log_to_google_sheets({"ID":generate_unique_id(),"Discord Handle":message.author.display_name,"User Query":user_message,"Bot Response":response,"Time Stamp":get_current_timestamp(),"Message Type":message_type,"Image URL":msg_images[0] if len(msg_images)==1 else "","Thread ID":threadId,"User Id":userId,"Message Id":messageId})

            #Log to a file
            log_to_csv({"ID":generate_unique_id(),"Discord Handle":message.author.display_name,"User Query":user_message,"Bot Response":response,"Time Stamp":get_current_timestamp(),"Message Type":message_type,"Image URL":msg_images[0] if len(msg_images)==1 else "","Thread ID":threadId,"User Id":userId,"Message Id":messageId})

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
                    # Store the display name of the author
                    display_name=message.author.display_name
                    # Create a thread for the response if it's in a guild
                    thread_name = f"{display_name}: {cleaned_message[:95-len(display_name)]}..." if (len(cleaned_message)+len(display_name)) > 100 else f"{display_name}: {cleaned_message}"
                    thread = await message.create_thread(name=f"{thread_name}", auto_archive_duration=60)
                    bot_created_threads[thread.id] = {'user_id': message.author.id, 'context': context}
                    for chunk in response_chunks:
                        await thread.send(chunk)
                else:
                    # Respond directly in DMs
                    for chunk in response_chunks:
                        await message.channel.send(chunk)
    except Exception as e:
        print(e)
        await message.channel.send("Sorry, something went wrong.")

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
