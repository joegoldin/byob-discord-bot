import asyncio
import os

import discord
from discord import Client, Intents
from dotenv import load_dotenv

from methods.createOldW2g import is_w2g_configured
from methods.createRoom import createRoom
from methods.queue import addToQueue
from methods.roomCheck import runRoomCheck
from responses import get_response
from roomState import rooms, w2g_rooms

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
serverUrl = os.getenv("BYOB_SERVER", "https://byob.video")

intents = Intents.default()
intents.message_content = True
intents.reactions = True
client = Client(intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} is now running!")
    await set_bot_status(status_text())

    while True:
        await asyncio.sleep(30)
        runRoomCheck(rooms)
        runRoomCheck(w2g_rooms, max_age_days=2)
        await set_bot_status(status_text())


async def set_bot_status(text):
    game = discord.Game(text)
    await client.change_presence(status=discord.Status.online, activity=game)


def status_text():
    return "type !w2 to start"


async def send_message(channel, content):
    try:
        await channel.send(content)
    except Exception as e:
        print(e)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    response = get_response(message.content)
    if response:
        await send_message(message.channel, response)


@client.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == "🚀":
        guild = client.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        # Ignore bot's own reactions
        if payload.user_id == client.user.id:
            return

        if "https://" in msg.content or "http://" in msg.content:
            if rooms:
                success = addToQueue(serverUrl, rooms, msg.content)
                if success:
                    await send_message(channel, "Added to queue! :rocket:")
                else:
                    await send_message(channel, "Failed to add to queue.")
            else:
                link = createRoom(serverUrl, rooms)
                addToQueue(serverUrl, rooms, msg.content)
                await send_message(
                    channel,
                    f"No active rooms found!\nCreated: {link}\nAdded to queue! :rocket:",
                )
        else:
            await send_message(channel, f"'{msg.content}' does not contain a link!")


def main():
    client.run(token=token)


if __name__ == "__main__":
    main()
