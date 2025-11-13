# Systemd Service - Automated Execution

## Overview

The Community Kit VPS edition includes systemd service files for automated execution every 2 hours. This enables continuous scanning and reporting without manual intervention.

## Components

### 1. Service File (`community-kit-vps.service`)
Defines how the scanner runs:
- Executes `get_repo_data_vps.py`
- Loads configuration from `config.env`
- Runs as oneshot (completes then exits)
- Includes security hardening
- Logs to systemd journal

### 2. Timer File (`community-kit-vps.timer`)
Schedules the service execution:
- Runs every 2 hours
- Starts 5 minutes after boot (if timer was missed)
- Randomizes start by up to 5 minutes (reduces load spikes)
- Persistent (tracks last run across reboots)

### 3. Installation Script (`install-systemd.sh`)
Automated installation:
- Copies files to `/opt/community_kit` (configurable)
- Installs Python dependencies
- Configures systemd service and timer
- Enables and starts the timer
- Provides status and usage information

## Quick Installation

### Prerequisites
- Root access (sudo)
- Python 3.8+
- Git
- Tor (optional, for hidden service support)

### Install

```bash
# Navigate to project directory
cd /path/to/community_kit

# Run installation script as root
sudo ./install-systemd.sh
```

The script will:
1. Prompt for installation directory (default: `/opt/community_kit`)
2. Copy all necessary files
3. Install Python dependencies
4. Configure systemd service and timer
5. Enable and start automatic execution

### Post-Installation

Edit the configuration file:
```bash
sudo nano /opt/community_kit/config.env
```

Ensure you configure:
- `GITHUB_TOKEN` - GitHub API token
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Telegram chat ID
- `HIDDEN_SERVICE_ADDRESS` - Your .onion address
- `HIDDEN_SERVICE_NAME` - Scanner name
- `USE_TOR` - Set to `true` for Tor proxy

## Manual Installation

If you prefer manual installation:

### 1. Copy Files

```bash
# Create installation directory
sudo mkdir -p /opt/community_kit

# Copy project files
sudo cp get_repo_data_vps.py /opt/community_kit/
sudo cp community_kit_downloader_vps.sh /opt/community_kit/
sudo cp requirements.txt /opt/community_kit/
sudo cp tracked_repos.txt /opt/community_kit/
sudo cp config.env.example /opt/community_kit/config.env

# Create reports directory
sudo mkdir -p /opt/community_kit/reports
```

### 2. Install Dependencies

```bash
sudo python3 -m pip install -r /opt/community_kit/requirements.txt
```

### 3. Configure

```bash
sudo nano /opt/community_kit/config.env
# Add your tokens and settings
```

### 4. Install Service Files

```bash
# Copy service file
sudo cp community-kit-vps.service /etc/systemd/system/

# Copy timer file
sudo cp community-kit-vps.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload
```

### 5. Enable and Start

```bash
# Enable timer (starts on boot)
sudo systemctl enable community-kit-vps.timer

# Start timer now
sudo systemctl start community-kit-vps.timer
```

## Usage

### Check Status

```bash
# Timer status
sudo systemctl status community-kit-vps.timer

# Service status (last run)
sudo systemctl status community-kit-vps.service
```

### View Logs

```bash
# Follow logs in real-time
sudo journalctl -u community-kit-vps.service -f

# View last 100 lines
sudo journalctl -u community-kit-vps.service -n 100

# View logs from today
sudo journalctl -u community-kit-vps.service --since today

# View logs with specific date
sudo journalctl -u community-kit-vps.service --since "2025-11-13 10:00:00"
```

### Manual Execution

Run the service manually (without waiting for timer):

```bash
sudo systemctl start community-kit-vps.service
```

### View Schedule

See next scheduled runs:

```bash
# All timers
systemctl list-timers

# Specific timer
systemctl list-timers community-kit-vps.timer
```

### Stop/Disable

```bash
# Stop timer (no more automatic runs)
sudo systemctl stop community-kit-vps.timer

# Disable timer (won't start on boot)
sudo systemctl disable community-kit-vps.timer

# Stop currently running service
sudo systemctl stop community-kit-vps.service
```

### Restart After Config Changes

If you modify `config.env`:

```bash
# Restart the timer to pick up changes
sudo systemctl restart community-kit-vps.timer

# Or reload systemd and restart
sudo systemctl daemon-reload
sudo systemctl restart community-kit-vps.timer
```

## Configuration

### Timer Schedule

The default schedule is every 2 hours. To change this, edit the timer file:

```bash
sudo nano /etc/systemd/system/community-kit-vps.timer
```

Change the `OnCalendar` line:

```ini
# Every hour
OnCalendar=hourly

# Every 4 hours
OnCalendar=*:0/4:00

# Every day at 2 AM
OnCalendar=daily
OnCalendar=*-*-* 02:00:00

# Every Monday at 3 AM
OnCalendar=Mon *-*-* 03:00:00

# Every 30 minutes
OnCalendar=*:0/30:00
```

After editing, reload systemd:
```bash
sudo systemctl daemon-reload
sudo systemctl restart community-kit-vps.timer
```

### Service Configuration

Edit service file for advanced settings:

```bash
sudo nano /etc/systemd/system/community-kit-vps.service
```

Options you might want to change:

```ini
# Working directory (where script runs)
WorkingDirectory=/opt/community_kit

# User (default is root, can change to specific user)
User=your_user

# Timeout (default 1 hour)
TimeoutStartSec=3600

# Memory limit (default 2GB)
MemoryLimit=2G

# CPU limit (percentage)
CPUQuota=50%
```

### Environment Variables

The service loads environment variables from `config.env`. You can also set them directly in the service file:

```ini
[Service]
Environment="USE_TOR=true"
Environment="HIDDEN_SERVICE_NAME=my_scanner"
EnvironmentFile=/opt/community_kit/config.env
```

## Monitoring

### Health Check Script

Create a monitoring script to check if the service is running properly:

```bash
#!/bin/bash

# Check timer status
if systemctl is-active --quiet community-kit-vps.timer; then
    echo "✅ Timer is active"
else
    echo "❌ Timer is not active"
    exit 1
fi

# Check last run
LAST_RUN=$(systemctl show community-kit-vps.service -p ActiveEnterTimestamp --value)
echo "Last run: $LAST_RUN"

# Check for errors in last run
ERRORS=$(journalctl -u community-kit-vps.service --since "2 hours ago" | grep -i error | wc -l)
if [ $ERRORS -gt 0 ]; then
    echo "⚠️  $ERRORS errors found in logs"
else
    echo "✅ No errors in recent logs"
fi
```

### Email Notifications

Configure systemd to send email on failure:

```bash
# Install sendmail or equivalent
sudo apt-get install mailutils

# Edit service file
sudo nano /etc/systemd/system/community-kit-vps.service
```

Add after `[Service]`:
```ini
OnFailure=status-email@%n.service
```

### Telegram Health Monitoring

The script already sends Telegram notifications on:
- Start of scan
- Completion with statistics
- Errors during execution
- Credential findings

## Security Considerations

### Service Hardening

The service includes security features:

```ini
# Isolated temporary directory
PrivateTmp=yes

# Prevent privilege escalation
NoNewPrivileges=true

# Read-only system directories
ProtectSystem=strict

# Restricted home directory access
ProtectHome=yes

# Only these directories are writable
ReadWritePaths=/opt/community_kit/reports /opt/community_kit/data.json
```

### Running as Non-Root User

For better security, run as a dedicated user:

```bash
# Create dedicated user
sudo useradd -r -s /bin/false community-kit

# Change ownership
sudo chown -R community-kit:community-kit /opt/community_kit

# Update service file
sudo nano /etc/systemd/system/community-kit-vps.service
```

Change:
```ini
User=community-kit
Group=community-kit
```

### Protecting Credentials

Ensure config file has restricted permissions:

```bash
sudo chmod 600 /opt/community_kit/config.env
sudo chown root:root /opt/community_kit/config.env
```

### Reports Directory

Protect reports containing sensitive data:

```bash
sudo chmod 700 /opt/community_kit/reports
sudo chown root:root /opt/community_kit/reports
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status community-kit-vps.service

# View detailed logs
sudo journalctl -u community-kit-vps.service -n 50 --no-pager

# Verify Python dependencies
python3 -c "import requests, git, dotenv" && echo "OK"

# Check configuration file
sudo cat /opt/community_kit/config.env

# Test script manually
cd /opt/community_kit
sudo python3 get_repo_data_vps.py
```

### Timer Not Running

```bash
# Check timer status
sudo systemctl status community-kit-vps.timer

# List all timers
systemctl list-timers --all

# Check timer logs
sudo journalctl -u community-kit-vps.timer

# Restart timer
sudo systemctl restart community-kit-vps.timer
```

### Permission Errors

```bash
# Check file ownership
ls -la /opt/community_kit/

# Fix ownership
sudo chown -R root:root /opt/community_kit/

# Check reports directory
ls -la /opt/community_kit/reports/

# Fix reports permissions
sudo chmod 755 /opt/community_kit/reports/
```

### High Resource Usage

```bash
# Check resource usage
systemctl show community-kit-vps.service -p MemoryCurrent -p CPUUsageNSec

# Adjust limits in service file
sudo nano /etc/systemd/system/community-kit-vps.service
```

Add or modify:
```ini
MemoryLimit=1G
CPUQuota=30%
```

### Tor Connection Issues

```bash
# Check Tor status
sudo systemctl status tor

# Test Tor connectivity
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip

# Restart Tor
sudo systemctl restart tor
```

## Advanced Usage

### Multiple Instances

Run multiple scanners with different configurations:

```bash
# Create separate directories
sudo mkdir -p /opt/community_kit_scanner1
sudo mkdir -p /opt/community_kit_scanner2

# Copy service files with different names
sudo cp community-kit-vps.service /etc/systemd/system/community-kit-vps-scanner1.service
sudo cp community-kit-vps.service /etc/systemd/system/community-kit-vps-scanner2.service

# Edit each service file to point to its directory
sudo nano /etc/systemd/system/community-kit-vps-scanner1.service

# Create corresponding timers
sudo cp community-kit-vps.timer /etc/systemd/system/community-kit-vps-scanner1.timer
sudo cp community-kit-vps.timer /etc/systemd/system/community-kit-vps-scanner2.timer

# Enable both
sudo systemctl enable community-kit-vps-scanner1.timer
sudo systemctl enable community-kit-vps-scanner2.timer
```

### Custom Scheduling

For complex scheduling, use calendar expressions:

```ini
# Weekdays at 9 AM and 5 PM
OnCalendar=Mon..Fri *-*-* 09:00:00
OnCalendar=Mon..Fri *-*-* 17:00:00

# First day of each month
OnCalendar=*-*-01 03:00:00

# Every 15 minutes during business hours
OnCalendar=Mon..Fri *-*-* 08..17:0/15:00
```

### Integration with Other Services

Chain services together:

```bash
# Edit service file
sudo nano /etc/systemd/system/community-kit-vps.service
```

Add dependencies:
```ini
[Unit]
After=tor.service postgresql.service
Requires=tor.service
```

## Uninstallation

To completely remove the systemd service:

```bash
# Stop and disable timer
sudo systemctl stop community-kit-vps.timer
sudo systemctl disable community-kit-vps.timer

# Stop service
sudo systemctl stop community-kit-vps.service

# Remove service files
sudo rm /etc/systemd/system/community-kit-vps.service
sudo rm /etc/systemd/system/community-kit-vps.timer

# Reload systemd
sudo systemctl daemon-reload

# Optionally remove installation directory
sudo rm -rf /opt/community_kit
```

## References

- [systemd.service documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [systemd.timer documentation](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)
- [systemd calendar time specification](https://www.freedesktop.org/software/systemd/man/systemd.time.html)

## Support

For issues with the systemd service:
1. Check logs: `sudo journalctl -u community-kit-vps.service -f`
2. Verify configuration: `sudo systemctl status community-kit-vps.timer`
3. Test manually: `sudo systemctl start community-kit-vps.service`
4. Review this documentation for troubleshooting steps

For general Community Kit VPS support, see:
- README_VPS.md
- VPS_SETUP.md
- CREDENTIAL_EXTRACTION.md
