# byob Discord Bot

A Discord bot for creating [byob.video](https://byob.video) watch party rooms and adding videos to the queue from Discord chat.

Based on [Watch2GetherBot](https://github.com/Bluskyfishing/Watch2GetherBot).

## Commands

| Command | Description |
|---------|-------------|
| `!byob [url]` | Create a room (optionally with a video) |
| `!q <url>` | Add a video to the queue |
| `🚀 reaction` | React to a message with a link to add it to the queue |
| `!byob c` | Show the current room |
| `!byob ls` | List all active rooms |
| `!byob set <n>` | Switch to a different active room |
| `!oldw2 [url]` | Create a legacy w2g.tv room (requires `W2G_API_KEY`) |
| `!help` | Show help |
| `!ver` | Show version |

`!w2` works as a shortcut for `!byob` (backwards compatible).

## Setup

### 1. Create a Discord bot

Go to https://discord.com/developers/applications and create a bot with these permissions:
- Send Messages
- Read Message History
- Add Reactions

### 2. Configure environment

Create a `.env` file:

```
DISCORD_TOKEN=your_discord_bot_token
BYOB_SERVER=https://byob.video
```

`BYOB_SERVER` defaults to `https://byob.video` if not set. Point it at your own instance if self-hosting.

### 3. Run

**With Docker:**
```bash
docker build -t byob-bot .
docker run -d --env-file .env byob-bot
```

**Without Docker:**
```bash
pip install -r requirements.txt
python main.py
```

## How it works

The bot uses the [byob REST API](https://byob.video/api) to create rooms and manage queues. No external keys are required for the core flow — byob handles all metadata fetching server-side.

## License

MIT
