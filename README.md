# 🎵 Advanced Discord Music Bot

Full-featured Discord music bot with hybrid commands (prefix $ and slash /), audio effects, multi-source support, and 24/7 voice capability.

## ✨ Features

### Core Features
- ✅ **Hybrid Commands** - Both prefix ($) and slash (/) commands
- ✅ **Multi-Source** - YouTube, YouTube Music, SoundCloud
- ✅ **High Quality Audio** - Opus codec, best quality
- ✅ **Queue System** - Unlimited queue with history
- ✅ **24/7 Voice** - Stay in voice channel with auto-reconnect

### Music Features
- ✅ **Playback Control** - Play, pause, resume, skip, back
- ✅ **Audio Effects** - Nightcore, Bass Boost
- ✅ **Volume Control** - 0-200% volume range
- ✅ **Loop** - Loop song or entire queue
- ✅ **Shuffle** - Randomize queue
- ✅ **Lyrics** - Genius lyrics integration
- ✅ **Song Disambiguation** - Choose between multiple artists

### Advanced Features
- ✅ **Playlist Support** - Import full playlists
- ✅ **Source Selection** - Choose preferred platform
- ✅ **Queue Management** - Remove, clear, view
- ✅ **Now Playing** - Detailed song information
- ✅ **History** - Track played songs for back command

---

## 📋 Requirements

### System Requirements
- Python 3.10 or higher
- FFmpeg (for audio processing)
- 2GB RAM minimum
- Linux/Windows/macOS

### Python Packages
- discord.py >= 2.4.0
- yt-dlp
- PyNaCl
- lyricsgenius (optional)
- python-dotenv

---

## 🚀 Setup Tutorial

### Step 1: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Give it a name (e.g., "Music Bot")
4. Go to **"Bot"** tab on the left
5. Click **"Add Bot"**
6. Under **"Privileged Gateway Intents"**, enable:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
7. Click **"Reset Token"** and copy the token (save it somewhere safe!)

### Step 2: Invite Bot to Server

1. Go to **"OAuth2"** → **"URL Generator"**
2. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Select bot permissions:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Connect (Voice)
   - ✅ Speak (Voice)
   - ✅ Use Voice Activity
   - ✅ Manage Messages
4. Copy the generated URL and open it in browser
5. Select your server and authorize

### Step 3: Install Dependencies

#### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

#### Install Python Packages

```bash
# Navigate to bot directory
cd ~/discord-music-bot

# Install requirements
pip3 install -r requirements.txt
```

### Step 4: Configure Bot

1. Copy the example env file:
```bash
cp .env.example .env
```

2. Edit `.env` file:
```bash
nano .env
```

3. Add your Discord bot token:
```env
DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
```

4. (Optional) Add Genius API token for lyrics:
   - Go to [genius.com/api-clients](https://genius.com/api-clients)
   - Create new API client
   - Copy "Client Access Token"
   - Add to `.env`:
   ```env
   GENIUS_ACCESS_TOKEN=YOUR_GENIUS_TOKEN_HERE
   ```

### Step 5: Run the Bot

```bash
python3 bot.py
```

You should see:
```
INFO - Bot logged in as YourBotName (ID: ...)
INFO - Connected to X guild(s)
INFO - Prefix: $
INFO - Slash commands: Enabled
INFO - Synced X slash command(s)
```

### Step 6: Test the Bot

In Discord:

**Test prefix commands:**
```
$play test
$skip
$queue
```

**Test slash commands:**
Type `/` and you should see bot's commands in autocomplete

---

## 📖 Usage Guide

### Music Commands

#### Prefix Commands (Fast)
```
$play <song>        - Play song or add to queue
$pause              - Pause playback
$resume             - Resume playback
$skip               - Skip to next song
$back               - Go to previous song
$stop               - Stop and disconnect
$queue              - Show queue
$nowplaying         - Current song info
$volume <0-200>     - Set volume
$shuffle            - Shuffle queue
$loop               - Loop current song
$loopqueue          - Loop entire queue
```

#### Slash Commands (Autocomplete)
```
/play song: <name>     - Play song
/skip                  - Skip
/pause                 - Pause
/resume                - Resume
/stop                  - Stop
/queue                 - Show queue
/volume level: <#>     - Volume
```

### Effects
```
$nightcore          - Toggle nightcore effect
$bassboost          - Toggle bass boost
$effects            - Show active effects
$cleareffects       - Remove all effects
```

### Advanced
```
$source <platform>  - Set source (youtube/ytmusic/soundcloud)
$playlist <url>     - Add playlist
$lyrics [song]      - Show lyrics
$choose <number>    - Pick from search results
$clear              - Clear queue
$remove <#>         - Remove song from queue
```

### Voice Management
```
$voice join [channel]  - Join voice channel
$voice leave           - Leave voice channel
$voice stay            - Enable 24/7 mode
$voice status          - Show connection status
```

---

## 🎯 Examples

### Basic Usage
```
# Join voice channel and play
$voice join
$play lofi hip hop beats

# Control playback
$pause
$resume
$skip
```

### With Effects
```
$play phonk music
$nightcore          # Enable nightcore
$bassboost          # Enable bass boost
$volume 150         # Louder
$effects            # Check active effects
```

### Multiple Songs
```
$play song 1
$play song 2        # Added to queue
$play song 3        # Added to queue
$queue              # View queue
$shuffle            # Randomize
$loopqueue          # Loop all
```

### Song Disambiguation
```
$play never gonna give you up

# Bot shows multiple options:
# 1. Rick Astley - Never Gonna Give You Up
# 2. Various - Never Gonna Give You Up (Cover)

$choose 1           # Pick Rick Astley
```

### 24/7 Voice Mode
```
$voice join Lounge
$voice stay         # Bot will stay forever
$play music
```

### Lyrics
```
$play bohemian rhapsody
$lyrics             # Show current song lyrics
```

---

## 🔧 Configuration

### Bot Settings

Edit `bot.py`:
- **PREFIX** - Change command prefix (default: `$`)
- **INTENTS** - Modify bot intents

### Music Settings

Edit `cogs/music.py`:
- **MusicSource** - Add/remove music sources
- **AudioEffect** - Add custom audio effects
- **Volume range** - Change max volume

---

## 📂 Project Structure

```
discord-music-bot/
├── bot.py                 # Main bot file
├── cogs/
│   ├── __init__.py
│   ├── music.py          # Music commands
│   └── voice_manager.py  # Voice 24/7 support
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your tokens (create this)
├── .gitignore
└── README.md
```

---

## 🐛 Troubleshooting

### Bot not responding
- Check bot has proper permissions
- Verify message content intent is enabled
- Check bot is online in Discord

### Music not playing
- Install FFmpeg: `ffmpeg -version`
- Check bot has voice permissions
- Verify you're in a voice channel

### Slash commands not showing
- Wait 1 hour for Discord sync
- Restart Discord client
- Re-invite bot with `applications.commands` scope

### Lyrics not working
- Add GENIUS_ACCESS_TOKEN to .env
- Install lyricsgenius: `pip install lyricsgenius`

### Bot crashes
- Check logs in `bot.log`
- Verify Python version: `python3 --version` (need 3.10+)
- Update packages: `pip install -U -r requirements.txt`

---

## 🚀 Deployment

### Run in Background (Linux)

**Using screen:**
```bash
screen -S musicbot
python3 bot.py
# Press Ctrl+A then D to detach
```

**Using systemd:**

Create `/etc/systemd/system/musicbot.service`:
```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/discord-music-bot
ExecStart=/usr/bin/python3 /home/your_username/discord-music-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable musicbot
sudo systemctl start musicbot
sudo systemctl status musicbot
```

### Run on Windows

**Create `run.bat`:**
```batch
@echo off
python bot.py
pause
```

Double-click to run.

---

## 📝 Notes

- Bot requires Message Content Intent for prefix commands
- Slash commands may take up to 1 hour to sync globally
- Some YouTube videos may be region-restricted
- Very high quality uses more bandwidth
- 24/7 mode keeps bot connected even when idle

---

## 🎉 Features Summary

| Feature | Prefix | Slash |
|---------|--------|-------|
| Play music | ✅ | ✅ |
| Skip | ✅ | ✅ |
| Back | ✅ | ✅ |
| Volume 0-200% | ✅ | ✅ |
| Nightcore | ✅ | ✅ |
| Bass Boost | ✅ | ✅ |
| Lyrics | ✅ | ✅ |
| Multi-source | ✅ | ✅ |
| Playlist | ✅ | ✅ |
| Queue | ✅ | ✅ |
| Loop | ✅ | ✅ |
| Shuffle | ✅ | ✅ |
| 24/7 Voice | ✅ | ✅ |

---

## 📄 License

MIT License - Feel free to modify and use!

---

## 🙏 Credits

- discord.py - Discord API wrapper
- yt-dlp - YouTube downloader
- FFmpeg - Audio processing
- Genius - Lyrics API

---

## 💡 Tips

**For beginners:**
- Use slash commands (/) for autocomplete
- Start with basic play/pause/skip
- Enable 24/7 mode for always-on bot

**For power users:**
- Use prefix commands ($) for speed
- Shortcuts: $s (skip), $q (queue), $np (nowplaying)
- Combine effects for unique sound

**Best practices:**
- Set volume to 100% by default
- Use source selection for best quality
- Enable loop queue for continuous playback
- Use disambiguation to pick correct artist

---

## 🔄 Updates

To update dependencies:
```bash
pip install -U -r requirements.txt
```

To update yt-dlp (recommended monthly):
```bash
pip install -U yt-dlp
```

---

**Enjoy your music bot! 🎵🎉**
