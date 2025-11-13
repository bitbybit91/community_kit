# Community Kit - VPS Edition

Enhanced version of the Cobalt Strike Community Kit with Tor hidden service support and Telegram notifications for VPS deployment.

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/bitbybit91/community_kit.git
cd community_kit
pip3 install -r requirements.txt
```

### 2. Configure
```bash
cp config.env.example config.env
nano config.env  # Add your tokens and settings
```

### 3. Run
```bash
# Update repository data
python3 get_repo_data_vps.py

# Download all repositories
./community_kit_downloader_vps.sh
```

## ✨ Features

### What's New in VPS Edition

- **🔧 Bug Fixes**: All known bugs in the original code have been fixed
- **🧅 Tor Support**: Route all traffic through Tor for complete anonymity
- **📱 Telegram Notifications**: Real-time updates via Telegram bot
- **🔒 Secure Config**: Environment-based configuration management
- **📊 Better Logging**: Enhanced error reporting and progress tracking
- **🌐 Hidden Services**: Full support for VPS deployment with hidden services

### Bug Fixes Included

1. **Binary Check Fix** - Fixed list/string comparison bug in `contains_binary`
2. **Error Message Fix** - Fixed incorrect variable usage in error reporting
3. **Error Handling** - Added comprehensive try-catch blocks
4. **Git Proxy** - Proper Tor proxy configuration for git operations
5. **Cleanup** - Automatic cleanup of temporary directories

## 📋 Requirements

- **Python 3.8+** with pip
- **Git** 
- **Tor** (optional, for hidden service support)
- **GitHub Token** (recommended for higher API rate limits)
- **Telegram Bot Token** (for notifications)

## 🔧 Configuration

Edit `config.env` with your settings:

```bash
# GitHub API Token
GITHUB_TOKEN=your_token_here

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Tor Configuration
USE_TOR=true  # Set to 'false' to disable
TOR_PROXY_HOST=127.0.0.1
TOR_PROXY_PORT=9050

# Notifications
ENABLE_TELEGRAM_NOTIFICATIONS=true
TELEGRAM_NOTIFY_ON_SUCCESS=true
TELEGRAM_NOTIFY_ON_ERROR=true
```

## 📖 Documentation

- **[VPS_SETUP.md](VPS_SETUP.md)** - Complete setup guide with step-by-step instructions
- **[README.md](README.md)** - Original Community Kit documentation

## 🎯 Use Cases

### Standard Usage (Without Tor)
Perfect for regular GitHub synchronization with Telegram notifications:
```bash
USE_TOR=false python3 get_repo_data_vps.py
```

### Anonymous Usage (With Tor)
For complete anonymity on VPS with hidden services:
```bash
USE_TOR=true python3 get_repo_data_vps.py
```

### Automated Updates
Set up cron jobs for automatic daily updates:
```bash
0 2 * * * cd /opt/community_kit && python3 get_repo_data_vps.py
```

## 🔍 Scripts Overview

### get_repo_data_vps.py
Enhanced Python script that:
- Fetches GitHub repository data via API
- Clones repositories for analysis
- Detects binaries in projects
- Generates `data.json` with all information
- **NEW**: Supports Tor proxy for all operations
- **NEW**: Sends Telegram notifications on progress
- **FIXED**: All bugs from original version

### community_kit_downloader_vps.sh
Enhanced Bash script that:
- Downloads/updates all tracked repositories
- Maintains organized directory structure
- **NEW**: Tor proxy support for downloads
- **NEW**: Telegram notifications on completion
- **NEW**: Better error handling and reporting
- **NEW**: Update statistics and progress tracking

## 🛡️ Security Features

1. **Environment-based Secrets** - No hardcoded tokens in code
2. **Tor Integration** - Complete anonymity through Tor network
3. **Secure File Permissions** - Config files protected with proper permissions
4. **Rate Limit Handling** - Respects GitHub API rate limits
5. **Error Recovery** - Graceful handling of network failures

## 📊 Output

### Success Notifications
When updates complete successfully, you'll receive:
- Total duration
- Number of repositories processed
- Number of updates applied
- Any errors encountered

### Error Notifications
On errors, you'll be notified with:
- Error description
- Failed repository name
- Suggestions for resolution

### Example Telegram Message
```
✅ Community Kit Update Complete

⏱ Duration: 45.2s
✅ Success: 125
❌ Errors: 0
🌐 Tor: Enabled
```

## 🔧 Troubleshooting

### Common Issues

**Tor Connection Failed**
```bash
sudo systemctl start tor
netstat -tlnp | grep 9050
```

**Telegram Bot Not Working**
```bash
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

**Python Dependencies Missing**
```bash
pip3 install -r requirements.txt
```

See **[VPS_SETUP.md](VPS_SETUP.md)** for detailed troubleshooting.

## 📜 License

Same as the original Community Kit project. See [LICENSE](LICENSE) file.

## 🤝 Credits

- **Original Project**: [Cobalt Strike Community Kit](https://github.com/Cobalt-Strike/community_kit)
- **VPS Enhancements**: Added Tor support, Telegram notifications, and bug fixes

## 📞 Support

For detailed setup instructions, see [VPS_SETUP.md](VPS_SETUP.md)

For the original Community Kit documentation, see [README.md](README.md)
