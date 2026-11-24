"""
Music Cog - Advanced music player with effects and multi-source support
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
from typing import Optional, List
from collections import deque
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
import os

logger = logging.getLogger('discord_bot.music')


class MusicSource(Enum):
    """Music source platforms."""
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "ytmusic"
    SOUNDCLOUD = "soundcloud"


class AudioEffect(Enum):
    """Audio effects."""
    NIGHTCORE = "nightcore"
    BASSBOOST = "bassboost"


@dataclass
class Song:
    """Song with metadata."""
    title: str
    artist: str
    url: str
    duration: int
    thumbnail: str
    requester: str
    webpage_url: str
    source: MusicSource
    album: Optional[str] = None
    year: Optional[int] = None
    
    @property
    def duration_str(self) -> str:
        if self.duration == 0:
            return "Live"
        td = timedelta(seconds=self.duration)
        h, r = divmod(td.seconds, 3600)
        m, s = divmod(r, 60)
        return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
    
    @property
    def display_name(self) -> str:
        if self.artist and self.artist.lower() not in self.title.lower():
            return f"{self.artist} - {self.title}"
        return self.title


class MusicPlayer:
    """Music player for a guild."""
    
    def __init__(self, voice_client: discord.VoiceClient, guild_id: int):
        self.voice_client = voice_client
        self.guild_id = guild_id
        self.queue: deque[Song] = deque()
        self.history: List[Song] = []
        self.current: Optional[Song] = None
        self.volume: float = 1.0
        self.is_playing: bool = False
        
        self.effects = {
            AudioEffect.NIGHTCORE: False,
            AudioEffect.BASSBOOST: False,
        }
        
        self.loop_song: bool = False
        self.loop_queue: bool = False
        self.preferred_source: MusicSource = MusicSource.YOUTUBE
    
    def get_ffmpeg_filters(self) -> str:
        """Get FFmpeg audio filter string."""
        filters = []
        if self.effects[AudioEffect.NIGHTCORE]:
            filters.append("asetrate=48000*1.25,aresample=48000")
        if self.effects[AudioEffect.BASSBOOST]:
            filters.append("bass=g=10,dynaudnorm")
        return ",".join(filters) if filters else ""
    
    async def play_next(self):
        """Play next song in queue."""
        if self.loop_song and self.current:
            song = self.current
        elif not self.queue:
            if self.loop_queue and self.history:
                self.queue = deque(self.history)
                song = self.queue.popleft()
            else:
                self.current = None
                self.is_playing = False
                return
        else:
            song = self.queue.popleft()
            self.current = song
            self.history.append(song)
        
        self.is_playing = True
        
        try:
            import yt_dlp
            
            ydl_opts = {
                'format': 'bestaudio[acodec=opus]/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song.url, download=False)
                url = info['url']
            
            ffmpeg_opts = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }
            
            audio_filter = self.get_ffmpeg_filters()
            if audio_filter:
                ffmpeg_opts['options'] += f' -af "{audio_filter}"'
            
            audio = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
            audio = discord.PCMVolumeTransformer(audio, volume=self.volume)
            
            self.voice_client.play(
                audio,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(), 
                    self.voice_client.loop
                )
            )
        except Exception as e:
            logger.error(f"Play error: {e}")
            self.is_playing = False
            await self.play_next()


class Music(commands.Cog):
    """Music commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players: dict[int, MusicPlayer] = {}
        self.pending_choices: dict[int, List[Song]] = {}
    
    def get_player(self, ctx) -> Optional[MusicPlayer]:
        """Get or create player for guild."""
        if not ctx.guild:
            return None
        
        if ctx.guild.id not in self.players:
            if ctx.guild.voice_client:
                self.players[ctx.guild.id] = MusicPlayer(ctx.guild.voice_client, ctx.guild.id)
            else:
                return None
        else:
            # Update voice client reference
            if ctx.guild.voice_client:
                self.players[ctx.guild.id].voice_client = ctx.guild.voice_client
        
        return self.players[ctx.guild.id]
    
    async def extract_songs(self, query: str, requester: str, source: MusicSource) -> List[Song]:
        """Extract songs from query."""
        try:
            import yt_dlp
            
            ydl_opts = {
                'format': 'bestaudio[acodec=opus]/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            if not query.startswith('http'):
                if source == MusicSource.SOUNDCLOUD:
                    query = f"scsearch5:{query}"
                else:
                    query = f"ytsearch5:{query}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                
                songs = []
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            song = self._create_song(entry, requester, source)
                            if song:
                                songs.append(song)
                else:
                    song = self._create_song(info, requester, source)
                    if song:
                        songs.append(song)
                
                return songs
        except Exception as e:
            logger.error(f"Extract error: {e}")
            return []
    
    def _create_song(self, info: dict, requester: str, source: MusicSource) -> Optional[Song]:
        """Create Song from yt-dlp info."""
        try:
            title = info.get('title', 'Unknown')
            artist = info.get('artist') or info.get('uploader', 'Unknown')
            
            if ' - ' in title and not info.get('artist'):
                parts = title.split(' - ', 1)
                artist = parts[0].strip()
                title = parts[1].strip()
            
            return Song(
                title=title,
                artist=artist,
                url=info.get('url', info.get('webpage_url', '')),
                duration=info.get('duration', 0),
                thumbnail=info.get('thumbnail', ''),
                requester=requester,
                webpage_url=info.get('webpage_url', ''),
                source=source,
                album=info.get('album'),
                year=int(info.get('upload_date', '0000')[:4]) if info.get('upload_date') else None,
            )
        except Exception as e:
            logger.error(f"Create song error: {e}")
            return None
    
    async def ensure_voice(self, ctx):
        """Ensure bot is in voice channel."""
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel!")
            return False
        
        if not ctx.guild.voice_client:
            try:
                await ctx.author.voice.channel.connect()
            except Exception as e:
                await ctx.send(f"❌ Failed to connect: {e}")
                return False
        elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
            await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
        
        return True
    
    # ============= PREFIX COMMANDS =============
    
    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx: commands.Context, *, query: str):
        """Play a song."""
        if not await self.ensure_voice(ctx):
            return
        
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ Player error")
            return
        
        await ctx.send(f"🔍 Searching: {query}...")
        
        songs = await self.extract_songs(query, ctx.author.display_name, player.preferred_source)
        
        if not songs:
            await ctx.send(f"❌ Not found: {query}")
            return
        
        # Disambiguation
        if len(songs) > 1 and not any(query.startswith(p) for p in ['http://', 'https://']):
            self.pending_choices[ctx.guild.id] = songs
            embed = discord.Embed(title="🎵 Multiple songs found", color=discord.Color.blue())
            
            for i, s in enumerate(songs[:5], 1):
                value = f"Duration: {s.duration_str}\nSource: {s.source.value}"
                if s.album:
                    value += f"\nAlbum: {s.album}"
                embed.add_field(name=f"{i}. {s.display_name}", value=value, inline=False)
            
            embed.set_footer(text="Type $choose <number> to select")
            await ctx.send(embed=embed)
            return
        
        # Add to queue
        for song in songs:
            player.queue.append(song)
        
        if not player.is_playing:
            await player.play_next()
            await ctx.send(f"🎵 **Now Playing:** {songs[0].display_name}\n⏱️ {songs[0].duration_str}")
        else:
            if len(songs) == 1:
                await ctx.send(f"➕ **Added:** {songs[0].display_name}\n📝 Position: #{len(player.queue)}")
            else:
                await ctx.send(f"➕ Added {len(songs)} songs to queue")
    
    @commands.command(name='choose')
    async def choose(self, ctx: commands.Context, number: int):
        """Choose from search results."""
        if ctx.guild.id not in self.pending_choices:
            await ctx.send("❌ No pending choices")
            return
        
        songs = self.pending_choices[ctx.guild.id]
        
        if number < 1 or number > len(songs):
            await ctx.send(f"❌ Invalid choice. Pick 1-{len(songs)}")
            return
        
        song = songs[number - 1]
        del self.pending_choices[ctx.guild.id]
        
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ Player error")
            return
        
        player.queue.append(song)
        
        if not player.is_playing:
            await player.play_next()
            await ctx.send(f"🎵 **Playing:** {song.display_name}")
        else:
            await ctx.send(f"➕ **Added:** {song.display_name}")
    
    @commands.command(name='skip', aliases=['s', 'next'])
    async def skip(self, ctx: commands.Context):
        """Skip current song."""
        player = self.get_player(ctx)
        if not player or not player.is_playing:
            await ctx.send("❌ Nothing playing")
            return
        
        player.voice_client.stop()
        await ctx.send("⏭️ Skipped!")
    
    @commands.command(name='back', aliases=['previous', 'prev'])
    async def back(self, ctx: commands.Context):
        """Go to previous song."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ No player")
            return
        
        if len(player.history) >= 2:
            player.history.pop()
            previous = player.history.pop()
            player.queue.appendleft(previous)
            player.voice_client.stop()
            await ctx.send("⏮️ Playing previous!")
        else:
            await ctx.send("❌ No previous song")
    
    @commands.command(name='pause')
    async def pause(self, ctx: commands.Context):
        """Pause playback."""
        player = self.get_player(ctx)
        if player and player.voice_client.is_playing():
            player.voice_client.pause()
            await ctx.send("⏸️ Paused")
        else:
            await ctx.send("❌ Nothing playing")
    
    @commands.command(name='resume')
    async def resume(self, ctx: commands.Context):
        """Resume playback."""
        player = self.get_player(ctx)
        if player and player.voice_client.is_paused():
            player.voice_client.resume()
            await ctx.send("▶️ Resumed")
        else:
            await ctx.send("❌ Nothing paused")
    
    @commands.command(name='stop')
    async def stop(self, ctx: commands.Context):
        """Stop and disconnect."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ Nothing playing")
            return
        
        player.queue.clear()
        player.history.clear()
        if player.voice_client.is_playing():
            player.voice_client.stop()
        
        await ctx.guild.voice_client.disconnect()
        del self.players[ctx.guild.id]
        await ctx.send("⏹️ Stopped")
    
    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx: commands.Context):
        """Show queue."""
        player = self.get_player(ctx)
        if not player or (not player.current and not player.queue):
            await ctx.send("📝 Queue is empty")
            return
        
        embed = discord.Embed(title="📝 Music Queue", color=discord.Color.blue())
        
        if player.current:
            effects = [n.value for n, e in player.effects.items() if e]
            effects_str = f"\n🎛️ {', '.join(effects)}" if effects else ""
            loop_str = "\n🔂 Looping" if player.loop_song else ("\n🔁 Loop queue" if player.loop_queue else "")
            
            embed.add_field(
                name="🎵 Now Playing",
                value=f"{player.current.display_name}\n⏱️ {player.current.duration_str} | 👤 {player.current.requester}{effects_str}{loop_str}",
                inline=False
            )
        
        if player.queue:
            queue_text = ""
            for i, song in enumerate(list(player.queue)[:10], 1):
                queue_text += f"{i}. {song.display_name} ({song.duration_str})\n"
            
            if len(player.queue) > 10:
                queue_text += f"\n...and {len(player.queue) - 10} more"
            
            embed.add_field(name="📋 Up Next", value=queue_text, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='nowplaying', aliases=['np'])
    async def nowplaying(self, ctx: commands.Context):
        """Show current song."""
        player = self.get_player(ctx)
        if not player or not player.current:
            await ctx.send("❌ Nothing playing")
            return
        
        song = player.current
        embed = discord.Embed(title="🎵 Now Playing", color=discord.Color.blue())
        embed.add_field(name="Title", value=song.display_name, inline=False)
        embed.add_field(name="Duration", value=song.duration_str, inline=True)
        embed.add_field(name="Requested by", value=song.requester, inline=True)
        embed.add_field(name="Source", value=song.source.value, inline=True)
        embed.add_field(name="Volume", value=f"{int(player.volume * 100)}%", inline=True)
        
        effects = [n.value for n, e in player.effects.items() if e]
        if effects:
            embed.add_field(name="Effects", value=", ".join(effects), inline=False)
        
        if song.thumbnail:
            embed.set_thumbnail(url=song.thumbnail)
        
        embed.add_field(name="Link", value=song.webpage_url, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx: commands.Context, level: int = None):
        """Set volume (0-200)."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ No player")
            return
        
        if level is None:
            await ctx.send(f"🔊 Volume: {int(player.volume * 100)}%")
            return
        
        if level < 0 or level > 200:
            await ctx.send("❌ Volume must be 0-200")
            return
        
        player.volume = level / 100.0
        if player.voice_client.source:
            player.voice_client.source.volume = player.volume
        
        await ctx.send(f"🔊 Volume: {level}%")
    
    @commands.command(name='shuffle')
    async def shuffle(self, ctx: commands.Context):
        """Shuffle queue."""
        player = self.get_player(ctx)
        if not player or len(player.queue) < 2:
            await ctx.send("❌ Need 2+ songs")
            return
        
        import random
        queue_list = list(player.queue)
        random.shuffle(queue_list)
        player.queue = deque(queue_list)
        
        await ctx.send(f"🔀 Shuffled {len(player.queue)} songs")
    
    @commands.command(name='loop')
    async def loop(self, ctx: commands.Context):
        """Toggle loop song."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ Nothing playing")
            return
        
        player.loop_song = not player.loop_song
        
        if player.loop_song:
            await ctx.send(f"🔂 Looping: {player.current.display_name if player.current else 'current'}")
        else:
            await ctx.send("🔁 Loop off")
    
    @commands.command(name='loopqueue')
    async def loopqueue(self, ctx: commands.Context):
        """Toggle loop queue."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ No queue")
            return
        
        player.loop_queue = not player.loop_queue
        await ctx.send(f"🔁 Queue loop: {'ON ✅' if player.loop_queue else 'OFF ❌'}")
    
    @commands.command(name='nightcore')
    async def nightcore(self, ctx: commands.Context):
        """Toggle nightcore effect."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ No player")
            return
        
        player.effects[AudioEffect.NIGHTCORE] = not player.effects[AudioEffect.NIGHTCORE]
        enabled = player.effects[AudioEffect.NIGHTCORE]
        
        if player.is_playing:
            player.voice_client.stop()
        
        await ctx.send(f"🎶 **Nightcore:** {'ON ✅' if enabled else 'OFF ❌'}")
    
    @commands.command(name='bassboost')
    async def bassboost(self, ctx: commands.Context):
        """Toggle bass boost."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ No player")
            return
        
        player.effects[AudioEffect.BASSBOOST] = not player.effects[AudioEffect.BASSBOOST]
        enabled = player.effects[AudioEffect.BASSBOOST]
        
        if player.is_playing:
            player.voice_client.stop()
        
        await ctx.send(f"🔊 **Bass Boost:** {'ON ✅' if enabled else 'OFF ❌'}")
    
    @commands.command(name='effects')
    async def effects(self, ctx: commands.Context):
        """Show active effects."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ No player")
            return
        
        active = [n.value for n, e in player.effects.items() if e]
        
        if active:
            await ctx.send(f"🎛️ **Active Effects:** {', '.join(active)}")
        else:
            await ctx.send("🎛️ No effects active")
    
    @commands.command(name='cleareffects')
    async def cleareffects(self, ctx: commands.Context):
        """Clear all effects."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ No player")
            return
        
        for effect in player.effects:
            player.effects[effect] = False
        
        if player.is_playing:
            player.voice_client.stop()
        
        await ctx.send("🎛️ Effects cleared")
    
    @commands.command(name='source')
    async def source(self, ctx: commands.Context, platform: str = None):
        """Set preferred source."""
        player = self.get_player(ctx)
        
        if not platform:
            current = player.preferred_source.value if player else "youtube"
            await ctx.send(f"🎵 Current source: **{current}**\nAvailable: youtube, ytmusic, soundcloud")
            return
        
        source_map = {
            'youtube': MusicSource.YOUTUBE, 'yt': MusicSource.YOUTUBE,
            'ytmusic': MusicSource.YOUTUBE_MUSIC, 'youtubemusic': MusicSource.YOUTUBE_MUSIC,
            'soundcloud': MusicSource.SOUNDCLOUD, 'sc': MusicSource.SOUNDCLOUD,
        }
        
        source = source_map.get(platform.lower())
        if not source:
            await ctx.send("❌ Invalid source. Use: youtube, ytmusic, soundcloud")
            return
        
        if player:
            player.preferred_source = source
            await ctx.send(f"✅ Source: **{source.value}**")
        else:
            await ctx.send("❌ No active player")
    
    @commands.command(name='lyrics')
    async def lyrics(self, ctx: commands.Context, *, song: str = None):
        """Show lyrics."""
        if not song:
            player = self.get_player(ctx)
            if player and player.current:
                song = f"{player.current.artist} {player.current.title}"
            else:
                await ctx.send("❌ No song playing or specified")
                return
        
        try:
            import lyricsgenius
            
            token = os.getenv('GENIUS_ACCESS_TOKEN')
            if not token:
                await ctx.send("❌ Genius API token not configured")
                return
            
            genius = lyricsgenius.Genius(token, verbose=False, remove_section_headers=True)
            result = genius.search_song(song)
            
            if result and result.lyrics:
                lyrics = result.lyrics
                if len(lyrics) > 1900:
                    lyrics = lyrics[:1900] + "\n\n...(truncated)"
                
                embed = discord.Embed(
                    title=f"🎤 {result.title}",
                    description=f"by {result.artist}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Lyrics", value=f"```\n{lyrics}\n```", inline=False)
                embed.add_field(name="Link", value=result.url, inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Lyrics not found: {song}")
        except ImportError:
            await ctx.send("❌ Install lyricsgenius: `pip install lyricsgenius`")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
    
    @commands.command(name='clear')
    async def clear_queue(self, ctx: commands.Context):
        """Clear queue."""
        player = self.get_player(ctx)
        if not player:
            await ctx.send("❌ Queue empty")
            return
        
        size = len(player.queue)
        player.queue.clear()
        await ctx.send(f"🗑️ Cleared {size} songs")
    
    @commands.command(name='remove')
    async def remove(self, ctx: commands.Context, position: int):
        """Remove song from queue."""
        player = self.get_player(ctx)
        if not player or position < 1 or position > len(player.queue):
            await ctx.send("❌ Invalid position")
            return
        
        song = list(player.queue)[position - 1]
        queue_list = list(player.queue)
        queue_list.pop(position - 1)
        player.queue = deque(queue_list)
        
        await ctx.send(f"🗑️ Removed: {song.display_name}")
    
    # ============= SLASH COMMANDS =============
    
    @app_commands.command(name="play", description="Play a song")
    @app_commands.describe(song="Song name or URL")
    async def play_slash(self, interaction: discord.Interaction, song: str):
        """Slash command for play."""
        await interaction.response.defer()
        
        # Create fake context
        ctx = await self.bot.get_context(interaction.message or interaction)
        ctx.author = interaction.user
        ctx.guild = interaction.guild
        ctx.channel = interaction.channel
        
        # Reuse prefix command
        await self.play(ctx, query=song)
    
    # Add more slash commands as needed...


async def setup(bot: commands.Bot):
    """Setup function for cog."""
    await bot.add_cog(Music(bot))
