"""
Advanced Discord Music Bot
Features:
- Hybrid commands (prefix $ and slash /)
- Multi-source (YouTube, YouTube Music, SoundCloud)
- Audio effects (Nightcore, Bass Boost)
- Genius lyrics integration
- Song disambiguation
- Voice 24/7 support
- Very high quality audio
"""

import discord
from discord.ext import commands
import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')

# Bot configuration
PREFIX = "$"
INTENTS = discord.Intents.all()

class MusicBot(commands.Bot):
    """Main bot class."""
    
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=INTENTS,
            help_command=None,
            case_insensitive=True
        )
        
        self.logger = logger
        
    async def setup_hook(self):
        """Called when bot is starting."""
        # Load cogs
        await self.load_cogs()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def load_cogs(self):
        """Load all cogs."""
        cogs = [
            'cogs.music',
            'cogs.voice_manager',
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load {cog}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'Bot logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guild(s)')
        logger.info(f'Prefix: {PREFIX}')
        logger.info(f'Slash commands: Enabled')
        
        # Set activity
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{PREFIX}play | /play"
        )
        await self.change_presence(activity=activity)
    
    async def on_message(self, message: discord.Message):
        """Process messages."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Process commands
        await self.process_commands(message)
    
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: {error.param.name}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send(f"❌ Error: {error}")


def main():
    """Main entry point."""
    # Check for token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in .env file!")
        return
    
    # Create and run bot
    bot = MusicBot()
    
    try:
        bot.run(token, log_handler=None)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")


if __name__ == "__main__":
    main()
