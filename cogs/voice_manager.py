"""
Voice Manager Cog - 24/7 voice channel support
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging

logger = logging.getLogger('discord_bot.voice')


class VoiceManager(commands.Cog):
    """Voice channel management."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.stay_connected_guilds = set()
        self.reconnect_tasks = {}
    
    @commands.command(name='voice')
    async def voice_command(self, ctx: commands.Context, action: str = None, *, args: str = None):
        """Voice channel commands."""
        if not action:
            await ctx.send(self._get_help())
            return
        
        action = action.lower()
        
        if action == 'join':
            await self._join(ctx, args)
        elif action == 'leave':
            await self._leave(ctx)
        elif action == 'stay':
            await self._stay(ctx)
        elif action == 'status':
            await self._status(ctx)
        else:
            await ctx.send(self._get_help())
    
    async def _join(self, ctx: commands.Context, channel_name: str = None):
        """Join voice channel."""
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel!")
            return
        
        target_channel = None
        
        if channel_name:
            # Find by name
            for channel in ctx.guild.voice_channels:
                if channel.name.lower() == channel_name.lower():
                    target_channel = channel
                    break
            
            if not target_channel:
                await ctx.send(f"❌ Voice channel '{channel_name}' not found")
                return
        else:
            # Join user's channel
            target_channel = ctx.author.voice.channel
        
        # Connect
        if ctx.guild.voice_client:
            if ctx.guild.voice_client.channel.id == target_channel.id:
                await ctx.send(f"ℹ️ Already in **{target_channel.name}**")
                return
            else:
                await ctx.guild.voice_client.move_to(target_channel)
                await ctx.send(f"🔄 Moved to **{target_channel.name}**")
        else:
            try:
                await target_channel.connect()
                await ctx.send(f"✅ Joined **{target_channel.name}**\n💡 Use `$voice stay` for 24/7 mode")
            except Exception as e:
                await ctx.send(f"❌ Failed to join: {e}")
    
    async def _leave(self, ctx: commands.Context):
        """Leave voice channel."""
        if not ctx.guild.voice_client:
            await ctx.send("ℹ️ Not connected to any voice channel")
            return
        
        # Disable stay mode
        if ctx.guild.id in self.stay_connected_guilds:
            self.stay_connected_guilds.remove(ctx.guild.id)
        
        # Cancel reconnect task
        if ctx.guild.id in self.reconnect_tasks:
            self.reconnect_tasks[ctx.guild.id].cancel()
            del self.reconnect_tasks[ctx.guild.id]
        
        channel_name = ctx.guild.voice_client.channel.name
        await ctx.guild.voice_client.disconnect()
        
        await ctx.send(f"👋 Left **{channel_name}**")
    
    async def _stay(self, ctx: commands.Context):
        """Enable 24/7 mode."""
        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected():
            await ctx.send(f"❌ Not connected. Use `$voice join` first")
            return
        
        channel = ctx.guild.voice_client.channel
        
        # Enable stay mode
        self.stay_connected_guilds.add(ctx.guild.id)
        self._setup_reconnect_monitor(ctx.guild.id, channel.id)
        
        await ctx.send(f"✅ **24/7 Mode Enabled**\n📍 Bot will stay in **{channel.name}** and auto-reconnect if disconnected")
    
    async def _status(self, ctx: commands.Context):
        """Show voice status."""
        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected():
            await ctx.send("📊 **Voice Status:** Not connected")
            return
        
        voice_client = ctx.guild.voice_client
        channel = voice_client.channel
        stay_mode = ctx.guild.id in self.stay_connected_guilds
        
        embed = discord.Embed(title="📊 Voice Connection Status", color=discord.Color.blue())
        embed.add_field(name="🔊 Channel", value=f"**{channel.name}**", inline=False)
        embed.add_field(name="🆔 Channel ID", value=f"`{channel.id}`", inline=False)
        embed.add_field(name="📡 Connected", value="**Yes**", inline=True)
        embed.add_field(name="⏰ 24/7 Mode", value=f"**{'Enabled ✅' if stay_mode else 'Disabled ❌'}**", inline=True)
        embed.add_field(name="👥 Members in channel", value=f"**{len(channel.members)}**", inline=True)
        
        if hasattr(voice_client, 'latency'):
            embed.add_field(name="🎤 Latency", value=f"**{voice_client.latency * 1000:.1f}ms**", inline=True)
        
        await ctx.send(embed=embed)
    
    def _setup_reconnect_monitor(self, guild_id: int, channel_id: int):
        """Setup reconnect monitoring."""
        if guild_id in self.reconnect_tasks:
            self.reconnect_tasks[guild_id].cancel()
        
        async def monitor():
            while guild_id in self.stay_connected_guilds:
                await asyncio.sleep(10)
                
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    break
                
                if not guild.voice_client or not guild.voice_client.is_connected():
                    # Reconnect
                    logger.info(f"Reconnecting to guild {guild_id}")
                    try:
                        channel = guild.get_channel(channel_id)
                        if channel and isinstance(channel, discord.VoiceChannel):
                            await channel.connect()
                            logger.info(f"Reconnected to {channel.name}")
                    except Exception as e:
                        logger.error(f"Failed to reconnect: {e}")
                        await asyncio.sleep(30)
        
        task = asyncio.create_task(monitor())
        self.reconnect_tasks[guild_id] = task
    
    def _get_help(self) -> str:
        """Get help text."""
        return """🎤 **Voice Commands**

**$voice join [channel]** - Join voice channel
**$voice leave** - Leave voice channel
**$voice stay** - Enable 24/7 mode
**$voice status** - Show connection status

**Examples:**
• `$voice join General` - Join "General" voice
• `$voice join` - Join your current channel
• `$voice stay` - Stay in channel 24/7"""


async def setup(bot: commands.Bot):
    """Setup function for cog."""
    await bot.add_cog(VoiceManager(bot))
