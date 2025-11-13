# VPS Setup Guide - Community Kit with Hidden Service Support

This guide will help you set up the Community Kit on a VPS with Tor hidden service support and Telegram notifications.

## Features

- ✅ **Bug-free operation** - Fixed all known bugs in the original code
- 🧅 **Tor Hidden Service Support** - Route all traffic through Tor for anonymity
- 📱 **Telegram Notifications** - Get real-time updates about repository syncing
- 🔒 **Secure Configuration** - Environment-based configuration for secrets
- 📊 **Enhanced Logging** - Better error handling and status reporting
- 🚀 **VPS Optimized** - Designed for automated deployment on remote servers

## Prerequisites

### System Requirements
- Ubuntu/Debian-based VPS (or any Linux distribution)
- Python 3.8 or higher
- Git
- Tor (optional, for hidden service support)
- Bash
- curl

### API Requirements
- GitHub API token (recommended for higher rate limits)
- Telegram Bot Token (for notifications)
- Telegram Chat ID (where to send notifications)

## Installation Steps

### 1. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install Required Packages
```bash
# Install Python and Git
sudo apt-get install -y python3 python3-pip git curl

# Install Tor (optional, for hidden service support)
sudo apt-get install -y tor
```

### 3. Clone Repository
```bash
cd /opt
git clone https://github.com/bitbybit91/community_kit.git
cd community_kit
```

### 4. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 5. Configure Tor (Optional)

If you want to use Tor hidden services:

```bash
# Start Tor service
sudo systemctl start tor
sudo systemctl enable tor

# Verify Tor is running
sudo systemctl status tor

# Check Tor SOCKS proxy (should be listening on 9050)
netstat -tlnp | grep 9050
```

Edit Tor configuration for hidden services (optional):
```bash
sudo nano /etc/tor/torrc
```

Add the following lines:
```
# Enable SOCKS proxy
SOCKSPort 9050

# Optional: Create a hidden service
HiddenServiceDir /var/lib/tor/community_kit/
HiddenServicePort 80 127.0.0.1:8080
```

Restart Tor:
```bash
sudo systemctl restart tor
```

Get your onion address (if configured hidden service):
```bash
sudo cat /var/lib/tor/community_kit/hostname
```

### 6. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Save the **Bot Token** you receive

### 7. Get Telegram Chat ID

1. Start a chat with your bot
2. Send any message to your bot
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `"chat":{"id":` in the response
5. Save this **Chat ID**

### 8. Configure Environment

Create your configuration file:
```bash
cd /opt/community_kit
cp config.env.example config.env
nano config.env
```

Edit the configuration:
```bash
# GitHub API Token (get from https://github.com/settings/tokens)
GITHUB_TOKEN=ghp_your_github_token_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Tor Configuration (set to 'true' to enable)
USE_TOR=true
TOR_PROXY_HOST=127.0.0.1
TOR_PROXY_PORT=9050

# Notification Settings
ENABLE_TELEGRAM_NOTIFICATIONS=true
TELEGRAM_NOTIFY_ON_SUCCESS=true
TELEGRAM_NOTIFY_ON_ERROR=true
TELEGRAM_NOTIFY_ON_UPDATE=true
```

**Security Note**: Protect your config file:
```bash
chmod 600 config.env
```

## Usage

### Manual Execution

#### Run Data Updater (Python Script)
```bash
cd /opt/community_kit
python3 get_repo_data_vps.py
```

This will:
- Fetch repository data from GitHub
- Clone repositories for analysis
- Generate `data.json` with repository information
- Send Telegram notifications on progress

#### Run Downloader (Bash Script)
```bash
cd /opt/community_kit
chmod +x community_kit_downloader_vps.sh
./community_kit_downloader_vps.sh
```

This will:
- Download all tracked repositories
- Update existing repositories
- Send Telegram notifications on completion

### Automated Execution (Cron)

Set up automatic updates:

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths as needed):

# Update data.json daily at 2 AM
0 2 * * * cd /opt/community_kit && /usr/bin/python3 get_repo_data_vps.py >> /var/log/community_kit_data.log 2>&1

# Download/update repositories daily at 3 AM
0 3 * * * cd /opt/community_kit && /bin/bash community_kit_downloader_vps.sh >> /var/log/community_kit_download.log 2>&1
```

### Systemd Service (Advanced)

Create a systemd service for automated updates:

```bash
sudo nano /etc/systemd/system/community-kit-updater.service
```

Add:
```ini
[Unit]
Description=Community Kit Data Updater
After=network.target tor.service

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/community_kit
ExecStart=/usr/bin/python3 /opt/community_kit/get_repo_data_vps.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create a timer:
```bash
sudo nano /etc/systemd/system/community-kit-updater.timer
```

Add:
```ini
[Unit]
Description=Run Community Kit Updater Daily
Requires=community-kit-updater.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable community-kit-updater.timer
sudo systemctl start community-kit-updater.timer
```

## Verification

### Test Tor Connection
```bash
# Test if Tor is working
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```

Should return JSON with `"IsTor": true`

### Test Telegram Bot
```bash
# Send a test message
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "<YOUR_CHAT_ID>", "text": "Test message from Community Kit VPS"}'
```

### Check Logs
```bash
# View Python script logs
tail -f /var/log/community_kit_data.log

# View downloader logs
tail -f /var/log/community_kit_download.log

# View systemd logs (if using systemd)
journalctl -u community-kit-updater.service -f
```

## Troubleshooting

### Tor Connection Issues
```bash
# Check Tor status
sudo systemctl status tor

# Check if SOCKS proxy is listening
netstat -tlnp | grep 9050

# Test Tor connectivity
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```

### Telegram Bot Issues
```bash
# Verify bot token and chat ID
curl "https://api.telegram.org/bot<BOT_TOKEN>/getMe"
curl "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates"
```

### Python Dependencies Issues
```bash
# Reinstall dependencies
pip3 install --upgrade -r requirements.txt

# Check installed packages
pip3 list | grep -E "requests|gitpython|telegram|dotenv|PySocks"
```

### GitHub API Rate Limits
- Without authentication: 60 requests/hour
- With authentication: 5000 requests/hour
- **Solution**: Use a GitHub personal access token

### Permission Errors
```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/community_kit
chmod +x community_kit_downloader_vps.sh
```

## Security Best Practices

1. **Protect Configuration Files**
   ```bash
   chmod 600 config.env
   ```

2. **Use Environment Variables** (instead of config.env in production)
   ```bash
   export GITHUB_TOKEN="your_token"
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   ```

3. **Rotate Tokens Regularly**
   - Regenerate GitHub tokens periodically
   - Create new Telegram bots if tokens are compromised

4. **Monitor Access**
   ```bash
   # Check login history
   last -a
   
   # Monitor Tor traffic
   sudo tail -f /var/log/tor/notices.log
   ```

5. **Firewall Configuration**
   ```bash
   # Allow only essential ports
   sudo ufw allow ssh
   sudo ufw enable
   ```

## Bug Fixes

This version includes fixes for the following bugs in the original code:

1. **Binary Check Bug** (Line 65)
   - **Original**: `if (bins == "")` - comparing list to string
   - **Fixed**: `if not bins` - properly checking empty list

2. **Error Message Bug** (Line 88)
   - **Original**: `print("ERROR: Can not access " + value)` - printing list object
   - **Fixed**: `print("ERROR: Can not access " + project)` - printing project string

3. **Missing Error Handling**
   - Added try-except blocks for network operations
   - Added proper timeout handling for requests
   - Added cleanup for temporary directories

4. **Git Proxy Configuration**
   - Added proper git configuration for Tor proxy
   - Added cleanup of git proxy settings after operations

## Features Comparison

| Feature | Original | VPS Version |
|---------|----------|-------------|
| GitHub API Support | ✅ | ✅ |
| Repository Cloning | ✅ | ✅ |
| Binary Detection | ⚠️ (buggy) | ✅ (fixed) |
| Error Handling | ⚠️ (basic) | ✅ (comprehensive) |
| Tor Support | ❌ | ✅ |
| Hidden Services | ❌ | ✅ |
| Telegram Notifications | ❌ | ✅ |
| Configuration Management | ❌ | ✅ |
| Progress Reporting | ⚠️ (basic) | ✅ (detailed) |
| VPS Optimized | ❌ | ✅ |

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Verify all configuration settings
4. Ensure all dependencies are installed

## License

Same as the original Community Kit project - see LICENSE file.
