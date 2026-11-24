# 🚀 QUICK START GUIDE

## ⚡ 5-Minute Setup

### 1. Get Bot Token (2 minutes)

1. Visit: https://discord.com/developers/applications
2. Click "New Application" → Name it → Create
3. Go to "Bot" → Click "Add Bot"
4. Enable these intents:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Click "Reset Token" → **Copy the token**

### 2. Invite Bot (1 minute)

1. Go to "OAuth2" → "URL Generator"
2. Select:
   - ✅ bot
   - ✅ applications.commands
3. Bot Permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Connect
   - ✅ Speak
   - ✅ Manage Messages
4. Copy URL → Open in browser → Select server → Authorize

### 3. Install (1 minute)

```bash
# Install FFmpeg
sudo apt install ffmpeg

# Install bot
cd ~/discord-music-bot
pip3 install -r requirements.txt

# Configure
cp .env.example .env
nano .env
# Paste your token: DISCORD_TOKEN=paste_here
# Save: Ctrl+X → Y → Enter
```

### 4. Run (1 minute)

```bash
python3 bot.py
```

Wait for: `Bot logged in as ...`

### 5. Test

In Discord:
```
$play test
```

✅ **Done!** Bot is working!

---

## 📝 Commands Cheat Sheet

### Essential
```
$play <song>    - Play music
$skip           - Next song
$pause          - Pause
$resume         - Resume
$stop           - Stop all
```

### Queue
```
$queue          - Show queue
$nowplaying     - Current song
```

### Effects
```
$volume 150     - Louder
$nightcore      - Speed up
$bassboost      - More bass
```

### Voice
```
$voice join     - Join your channel
$voice stay     - Stay 24/7
```

---

## 🔧 Troubleshooting

**Bot not responding?**
→ Check Message Content Intent is enabled

**Music not playing?**
→ Install FFmpeg: `sudo apt install ffmpeg`

**Slash commands not showing?**
→ Wait 1 hour or restart Discord

---

**That's it! Enjoy! 🎉**
