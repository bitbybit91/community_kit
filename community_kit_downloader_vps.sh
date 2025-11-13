#!/usr/bin/env bash

# Cobalt Strike Community Kit Updater - VPS Edition with Tor and Telegram Support
# Enhanced version with hidden service support and Telegram notifications

# Load configuration from config.env if it exists
if [ -f "config.env" ]; then
    source config.env
fi

# Configuration with defaults
USE_TOR=${USE_TOR:-false}
TOR_PROXY_HOST=${TOR_PROXY_HOST:-127.0.0.1}
TOR_PROXY_PORT=${TOR_PROXY_PORT:-9050}
ENABLE_TELEGRAM_NOTIFICATIONS=${ENABLE_TELEGRAM_NOTIFICATIONS:-true}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-}

# Variables
cwd=`pwd`
community_kit_path=$cwd/"cobaltstrike_community_kit"
community_kit_projects="https://raw.githubusercontent.com/Cobalt-Strike/community_kit/main/tracked_repos.txt"
community_kit_readme="https://raw.githubusercontent.com/Cobalt-Strike/community_kit/main/README.md"
community_kit_license="https://raw.githubusercontent.com/Cobalt-Strike/community_kit/main/LICENSE"

# Counters
success_count=0
error_count=0
update_count=0
start_time=$(date +%s)

# Function to send Telegram message
send_telegram_message() {
    local message="$1"
    
    if [ "$ENABLE_TELEGRAM_NOTIFICATIONS" = "true" ] && [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        local telegram_url="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"
        
        if [ "$USE_TOR" = "true" ]; then
            curl -s -x socks5h://${TOR_PROXY_HOST}:${TOR_PROXY_PORT} \
                -X POST "$telegram_url" \
                -H "Content-Type: application/json" \
                -d "{\"chat_id\": \"${TELEGRAM_CHAT_ID}\", \"text\": \"${message}\", \"parse_mode\": \"HTML\"}" > /dev/null 2>&1
        else
            curl -s -X POST "$telegram_url" \
                -H "Content-Type: application/json" \
                -d "{\"chat_id\": \"${TELEGRAM_CHAT_ID}\", \"text\": \"${message}\", \"parse_mode\": \"HTML\"}" > /dev/null 2>&1
        fi
    fi
}

# Function to download file with optional Tor proxy
download_file() {
    local url="$1"
    local output="$2"
    
    if [ "$USE_TOR" = "true" ]; then
        curl -s -x socks5h://${TOR_PROXY_HOST}:${TOR_PROXY_PORT} -O -A "Community Kit VPS" "$url" -o "$output"
    else
        curl -s -O -A "Community Kit VPS" "$url" -o "$output"
    fi
    
    return $?
}

# Function to configure git for Tor
configure_git_proxy() {
    if [ "$USE_TOR" = "true" ]; then
        git config --global http.proxy socks5h://${TOR_PROXY_HOST}:${TOR_PROXY_PORT}
        git config --global https.proxy socks5h://${TOR_PROXY_HOST}:${TOR_PROXY_PORT}
        echo "[*] Git configured to use Tor proxy"
    fi
}

# Function to reset git proxy configuration
reset_git_proxy() {
    if [ "$USE_TOR" = "true" ]; then
        git config --global --unset http.proxy
        git config --global --unset https.proxy
        echo "[*] Git proxy configuration reset"
    fi
}

# Start
echo "###################################################"
echo "##  COBALT STRIKE - VPS EDITION                   "
echo "##  Community Kit Download and Update Tool        "              
echo "##  With Tor Hidden Service Support               "
echo "##  https://github.com/Cobalt-Strike/community_kit"
echo "###################################################"
echo ""

if [ "$USE_TOR" = "true" ]; then
    echo "[*] Tor proxy enabled: ${TOR_PROXY_HOST}:${TOR_PROXY_PORT}"
    
    # Test Tor connectivity
    if [ -x "$(command -v nc)" ]; then
        nc -z -w 3 ${TOR_PROXY_HOST} ${TOR_PROXY_PORT} 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "[+] Tor proxy is reachable"
        else
            echo "[!] WARNING: Tor proxy is not reachable!"
            send_telegram_message "⚠️ <b>Warning:</b> Tor proxy at ${TOR_PROXY_HOST}:${TOR_PROXY_PORT} is not reachable"
        fi
    fi
fi

# Send start notification
send_telegram_message "🚀 <b>Community Kit Downloader Started</b>%0ATime: $(date '+%Y-%m-%d %H:%M:%S')%0ATor: $([ "$USE_TOR" = "true" ] && echo "Enabled" || echo "Disabled")"

# Configure git for Tor if enabled
configure_git_proxy

## Check if "community_kit" directory exists
echo "[*] Checking for Community Kit directory:" $community_kit_path
if [ -d $community_kit_path ]
then
    echo "[+] Checking for Community Kit directory: FOUND"
else
    echo "[-] Checking for Community Kit directory: NOT FOUND"
    echo "[*] Creating" $community_kit_path
    mkdir -p $community_kit_path
fi

## CD to community kit directory
cd $community_kit_path

## Pull latest list of Community Kit Projects
echo "[*] Downloading latest project list"
[ -e tracked_repos.txt ] && rm tracked_repos.txt

if [ "$USE_TOR" = "true" ]; then
    curl -s -x socks5h://${TOR_PROXY_HOST}:${TOR_PROXY_PORT} -A "Community Kit VPS" $community_kit_projects -o tracked_repos.txt
else
    curl -s -A "Community Kit VPS" $community_kit_projects -o tracked_repos.txt
fi

if [ ! -f tracked_repos.txt ]; then
    echo "[!] ERROR: Failed to download tracked_repos.txt"
    send_telegram_message "❌ <b>Error:</b> Failed to download tracked_repos.txt"
    reset_git_proxy
    exit 1
fi

## Pull latest Community Kit README
echo "[*] Downloading latest README"
[ -e README.md ] && rm README.md

if [ "$USE_TOR" = "true" ]; then
    curl -s -x socks5h://${TOR_PROXY_HOST}:${TOR_PROXY_PORT} -A "Community Kit VPS" $community_kit_readme -o README.md
else
    curl -s -A "Community Kit VPS" $community_kit_readme -o README.md
fi

## Pull latest Community Kit LICENSE
echo "[*] Downloading latest LICENSE"
[ -e LICENSE ] && rm LICENSE

if [ "$USE_TOR" = "true" ]; then
    curl -s -x socks5h://${TOR_PROXY_HOST}:${TOR_PROXY_PORT} -A "Community Kit VPS" $community_kit_license -o LICENSE
else
    curl -s -A "Community Kit VPS" $community_kit_license -o LICENSE
fi

## Clone or Update each repository

IFS=$'\n'       # make newlines the only separator
set -f          # disable globbing

for i in $(cat < "$community_kit_path/tracked_repos.txt"); do
    # Skip comments and empty lines
    [[ "$i" =~ ^#.*$ ]] && continue
    [ -z "$i" ] && continue

    cd $community_kit_path

    author=`echo "$i" | cut -d' ' -f2- | cut -d'/' -f1` 
    project=`echo "$i" | cut -d' ' -f2- | cut -d'/' -f2` 

    if [ -d $community_kit_path/$author/$project ]
    then
        # Project exists
        # Git pull
        echo "[+] Project (" $author/$project ") exists"
        echo "[*] Updating $author/$project"
        cd $community_kit_path/$author/$project
        
        # Check if there are updates
        git fetch --quiet --depth 1 2>/dev/null
        
        LOCAL=$(git rev-parse @)
        REMOTE=$(git rev-parse @{u} 2>/dev/null)
        
        if [ "$LOCAL" != "$REMOTE" ]; then
            git pull --quiet --depth 1
            if [ $? -eq 0 ]; then
                ((update_count++))
                ((success_count++))
                echo "[+] Updated: $author/$project"
            else
                ((error_count++))
                echo "[!] Failed to update: $author/$project"
            fi
        else
            ((success_count++))
            echo "[=] Already up-to-date: $author/$project"
        fi
        
    else
        # Project does not exist
        # Git Clone
        echo "[-] Project (" $author/$project ") does NOT exist"

        # Clone repo
        echo "[*] Cloning $author/$project"
        git clone --quiet --depth 1 https://github.com/$author/$project $community_kit_path/$author/$project
        
        if [ $? -eq 0 ]; then
            ((success_count++))
            echo "[+] Successfully cloned: $author/$project"
        else
            ((error_count++))
            echo "[!] Failed to clone: $author/$project"
        fi
    fi

done

# Reset git proxy configuration
reset_git_proxy

# Calculate duration
end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "####################################################"
echo "##         Update Summary                         ##"
echo "####################################################"
echo "[*] Duration: ${duration} seconds"
echo "[*] Success: ${success_count} repositories"
echo "[*] Updates: ${update_count} repositories"
echo "[*] Errors: ${error_count} repositories"
echo "[*] The Cobalt Strike Community Kit has been updated"
echo "[*] Community kit directory:" $community_kit_path
echo "####################################################"

# Send completion notification
if [ "$ENABLE_TELEGRAM_NOTIFICATIONS" = "true" ]; then
    summary_message="✅ <b>Community Kit Downloader Complete</b>%0A%0A⏱ Duration: ${duration}s%0A✅ Success: ${success_count}%0A🔄 Updated: ${update_count}%0A❌ Errors: ${error_count}%0A🌐 Tor: $([ "$USE_TOR" = "true" ] && echo "Enabled" || echo "Disabled")"
    send_telegram_message "$summary_message"
fi

# Exit with appropriate code
if [ $error_count -gt 0 ]; then
    exit 1
fi

exit 0
