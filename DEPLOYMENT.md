# 🚀 DEPLOYMENT GUIDE

Production deployment options for running bot 24/7.

---

## Option 1: systemd (Recommended for Linux)

Runs bot as system service with auto-restart.

### Setup

1. Edit service file:
```bash
nano musicbot.service
```

2. Replace `REPLACE_WITH_YOUR_USERNAME` with your username:
```ini
User=danangdwi
WorkingDirectory=/home/danangdwi/discord-music-bot
ExecStart=/usr/bin/python3 /home/danangdwi/discord-music-bot/bot.py
```

3. Install service:
```bash
sudo cp musicbot.service /etc/systemd/system/
sudo systemctl daemon-reload
```

4. Enable and start:
```bash
sudo systemctl enable musicbot
sudo systemctl start musicbot
```

### Management

```bash
# Check status
sudo systemctl status musicbot

# View logs
sudo journalctl -u musicbot -f

# Restart
sudo systemctl restart musicbot

# Stop
sudo systemctl stop musicbot

# Disable auto-start
sudo systemctl disable musicbot
```

---

## Option 2: screen (Simple)

Runs bot in detachable terminal session.

### Start

```bash
screen -S musicbot
cd ~/discord-music-bot
python3 bot.py
```

Detach: Press `Ctrl+A` then `D`

### Management

```bash
# Reattach
screen -r musicbot

# List sessions
screen -ls

# Kill session
screen -X -S musicbot quit
```

---

## Option 3: tmux (Alternative to screen)

Similar to screen but more features.

### Install

```bash
sudo apt install tmux
```

### Start

```bash
tmux new -s musicbot
cd ~/discord-music-bot
python3 bot.py
```

Detach: Press `Ctrl+B` then `D`

### Management

```bash
# Reattach
tmux attach -t musicbot

# List sessions
tmux ls

# Kill session
tmux kill-session -t musicbot
```

---

## Option 4: Docker (Advanced)

Run bot in container.

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

### Build and Run

```bash
docker build -t music-bot .
docker run -d --name musicbot --env-file .env music-bot
```

### Management

```bash
# View logs
docker logs -f musicbot

# Restart
docker restart musicbot

# Stop
docker stop musicbot

# Start
docker start musicbot
```

---

## Option 5: PM2 (Node.js Process Manager)

Good for managing multiple bots.

### Install

```bash
npm install -g pm2
```

### Create ecosystem.config.js

```javascript
module.exports = {
  apps: [{
    name: 'music-bot',
    script: 'bot.py',
    interpreter: 'python3',
    cwd: '/home/danangdwi/discord-music-bot',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      PYTHONUNBUFFERED: 1
    }
  }]
};
```

### Start

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Management

```bash
# Status
pm2 status

# Logs
pm2 logs music-bot

# Restart
pm2 restart music-bot

# Stop
pm2 stop music-bot

# Delete
pm2 delete music-bot
```

---

## Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| systemd | Auto-start on boot, integrated logs | Linux only | Production servers |
| screen | Simple, no setup | Manual restart | Quick testing |
| tmux | More features than screen | Manual restart | Development |
| Docker | Isolated, portable | More complex | Microservices |
| PM2 | Easy management, monitoring | Requires Node.js | Multiple bots |

---

## Monitoring

### Check if bot is running

```bash
# systemd
systemctl is-active musicbot

# screen
screen -ls | grep musicbot

# tmux
tmux ls | grep musicbot

# docker
docker ps | grep musicbot

# pm2
pm2 status music-bot
```

### View logs

```bash
# systemd
journalctl -u musicbot -f

# screen
screen -r musicbot  # (then view console)

# File logs (all methods)
tail -f ~/discord-music-bot/bot.log
```

---

## Auto-restart on Crash

All methods above auto-restart on crash except screen/tmux.

**For screen/tmux**, use this wrapper:

Create `run_forever.sh`:
```bash
#!/bin/bash
while true; do
    python3 bot.py
    echo "Bot crashed. Restarting in 5 seconds..."
    sleep 5
done
```

```bash
chmod +x run_forever.sh
screen -S musicbot ./run_forever.sh
```

---

## Remote Server (VPS/Cloud)

### Recommended Providers

**Budget:**
- DigitalOcean ($6/month)
- Vultr ($6/month)
- Linode ($5/month)
- Hetzner (€4.5/month)

**Free tier:**
- Oracle Cloud (always free)
- AWS Free Tier (12 months)
- Google Cloud (90 days)

### Minimum Specs

- 1 vCPU
- 1GB RAM
- 10GB Storage
- Ubuntu 22.04 LTS

### Quick Deploy

```bash
# SSH into server
ssh user@your-server-ip

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg git

# Clone/upload bot
git clone <your-repo> discord-music-bot
# or upload: scp -r discord-music-bot user@server:~/

# Install
cd discord-music-bot
pip3 install -r requirements.txt

# Configure
nano .env  # Add your token

# Run with systemd
sudo cp musicbot.service /etc/systemd/system/
sudo nano /etc/systemd/system/musicbot.service  # Edit paths
sudo systemctl daemon-reload
sudo systemctl enable musicbot
sudo systemctl start musicbot

# Check status
sudo systemctl status musicbot
```

---

## Security Best Practices

1. **Never commit .env to git**
   - Already in .gitignore
   - Use environment variables on server

2. **Keep dependencies updated**
   ```bash
   pip install -U -r requirements.txt
   ```

3. **Monitor logs for errors**
   ```bash
   tail -f bot.log
   ```

4. **Backup configuration**
   ```bash
   cp .env .env.backup
   ```

5. **Use firewall**
   ```bash
   sudo ufw allow ssh
   sudo ufw enable
   ```

---

## Troubleshooting Production

### Bot stops unexpectedly

**Check system resources:**
```bash
htop
free -h
df -h
```

**Check logs:**
```bash
journalctl -u musicbot -n 100
tail -100 bot.log
```

### High memory usage

**Add memory limit to systemd service:**
```ini
[Service]
MemoryMax=512M
```

**Or restart daily with cron:**
```bash
0 4 * * * systemctl restart musicbot
```

### Bot not starting

**Check permissions:**
```bash
ls -la ~/discord-music-bot/
```

**Check Python path:**
```bash
which python3
```

**Test manually:**
```bash
cd ~/discord-music-bot
python3 bot.py
```

---

## Performance Tips

1. **Use SSD storage** for faster audio processing
2. **Enable swapfile** if low RAM
3. **Use nearest VPS region** to Discord servers
4. **Limit queue size** to prevent memory issues
5. **Monitor CPU usage** during peak times

---

## Backup & Restore

### Backup

```bash
tar -czf musicbot-backup.tar.gz discord-music-bot/
```

### Restore

```bash
tar -xzf musicbot-backup.tar.gz
cd discord-music-bot
pip3 install -r requirements.txt
systemctl start musicbot
```

---

**Choose the deployment method that fits your needs! 🚀**
