#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced version with Tor Hidden Service and Telegram support
@author: joevest (original), modified for VPS with hidden service support
"""

import os
import json
import requests
from git import Repo
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables from config.env file if it exists
load_dotenv('config.env')

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Tor Configuration
USE_TOR = os.environ.get('USE_TOR', 'false').lower() == 'true'
TOR_PROXY_HOST = os.environ.get('TOR_PROXY_HOST', '127.0.0.1')
TOR_PROXY_PORT = os.environ.get('TOR_PROXY_PORT', '9050')

# Hidden Service Configuration
HIDDEN_SERVICE_ADDRESS = os.environ.get('HIDDEN_SERVICE_ADDRESS', 'unknown.onion')
HIDDEN_SERVICE_NAME = os.environ.get('HIDDEN_SERVICE_NAME', 'default')

# Notification Configuration
ENABLE_TELEGRAM = os.environ.get('ENABLE_TELEGRAM_NOTIFICATIONS', 'true').lower() == 'true'
NOTIFY_ON_SUCCESS = os.environ.get('TELEGRAM_NOTIFY_ON_SUCCESS', 'true').lower() == 'true'
NOTIFY_ON_ERROR = os.environ.get('TELEGRAM_NOTIFY_ON_ERROR', 'true').lower() == 'true'
NOTIFY_ON_UPDATE = os.environ.get('TELEGRAM_NOTIFY_ON_UPDATE', 'true').lower() == 'true'

api_url_base = "https://api.github.com/repos/"
tracked_repos = "tracked_repos.txt"
git_repo_base = "https://github.com/"
datajson = "data.json"

# Reports directory
reports_dir = "reports"
if not os.path.exists(reports_dir):
    os.makedirs(reports_dir)

jsonhead = '{"data" : ['
jsonfoot = ']}'

repo_data = []
error_messages = []
success_count = 0
error_count = 0

# Setup proxies for Tor if enabled
proxies = None
if USE_TOR:
    proxies = {
        'http': f'socks5h://{TOR_PROXY_HOST}:{TOR_PROXY_PORT}',
        'https': f'socks5h://{TOR_PROXY_HOST}:{TOR_PROXY_PORT}'
    }
    print(f"[*] Tor proxy enabled: {TOR_PROXY_HOST}:{TOR_PROXY_PORT}")

headers = {"authorization": "Bearer " + GITHUB_TOKEN} if GITHUB_TOKEN else {}


def send_telegram_message(message):
    """Send a message to Telegram bot"""
    if not ENABLE_TELEGRAM or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        # Use proxies if Tor is enabled
        response = requests.post(url, json=payload, proxies=proxies, timeout=30)
        
        if response.status_code != 200:
            print(f"[!] Failed to send Telegram message: {response.status_code}")
    except Exception as e:
        print(f"[!] Error sending Telegram message: {str(e)}")


def contains_binary(root):
    """Check if directory contains binary files"""
    hasBinaryList = []
    try:
        for root, dirs, files in os.walk(root):
            for f in files:
                if f.endswith((".exe", ".dll", ".o")):
                    hasBinaryList.append(f)
    except Exception as e:
        print(f"[!] Error checking for binaries: {str(e)}")
    
    return hasBinaryList


def extract_credentials(root):
    """Extract potential credentials from repository files"""
    import re
    
    credentials = {
        'usernames': [],
        'passwords': [],
        'api_keys': [],
        'tokens': [],
        'urls': [],
        'emails': [],
        'other_sensitive': []
    }
    
    # Patterns for credential detection
    patterns = {
        'username': [
            r'username["\s:=]+([^\s\'"]+)',
            r'user["\s:=]+([^\s\'"]+)',
            r'login["\s:=]+([^\s\'"]+)',
        ],
        'password': [
            r'password["\s:=]+([^\s\'"]+)',
            r'passwd["\s:=]+([^\s\'"]+)',
            r'pwd["\s:=]+([^\s\'"]+)',
        ],
        'api_key': [
            r'api[_-]?key["\s:=]+([^\s\'"]+)',
            r'apikey["\s:=]+([^\s\'"]+)',
        ],
        'token': [
            r'token["\s:=]+([^\s\'"]+)',
            r'auth[_-]?token["\s:=]+([^\s\'"]+)',
            r'access[_-]?token["\s:=]+([^\s\'"]+)',
        ],
        'email': [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ],
    }
    
    searchable_extensions = ['.txt', '.conf', '.config', '.ini', '.env', '.yml', '.yaml', 
                            '.json', '.xml', '.properties', '.sh', '.bat', '.ps1', '.py', 
                            '.js', '.php', '.java', '.c', '.cpp', '.cs', '.rb', '.go']
    
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip .git directory
            if '.git' in dirpath:
                continue
            
            for filename in filenames:
                # Only search text-based files
                if not any(filename.endswith(ext) for ext in searchable_extensions):
                    continue
                
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Search for usernames
                        for pattern in patterns['username']:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            credentials['usernames'].extend([m for m in matches if len(m) > 2 and len(m) < 50])
                        
                        # Search for passwords
                        for pattern in patterns['password']:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            credentials['passwords'].extend([m for m in matches if len(m) > 2 and len(m) < 50])
                        
                        # Search for API keys
                        for pattern in patterns['api_key']:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            credentials['api_keys'].extend([m for m in matches if len(m) > 10 and len(m) < 100])
                        
                        # Search for tokens
                        for pattern in patterns['token']:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            credentials['tokens'].extend([m for m in matches if len(m) > 10 and len(m) < 100])
                        
                        # Search for emails
                        for pattern in patterns['email']:
                            matches = re.findall(pattern, content)
                            credentials['emails'].extend(matches)
                        
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"[!] Error extracting credentials: {str(e)}")
    
    # Remove duplicates and clean up
    for key in credentials:
        credentials[key] = list(set(credentials[key]))
        # Remove common false positives
        credentials[key] = [item for item in credentials[key] if item.lower() not in 
                           ['example', 'test', 'admin', 'root', 'user', 'password', 'your_', 'your-', 'xxx', '***']]
    
    return credentials


def save_credentials_report(project_name, credentials, repo_data):
    """Save credentials to a JSON report file"""
    report_filename = os.path.join(reports_dir, f"{project_name.replace('/', '_')}_report.json")
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'hidden_service': HIDDEN_SERVICE_ADDRESS,
        'hidden_service_name': HIDDEN_SERVICE_NAME,
        'project': project_name,
        'credentials': credentials,
        'repository_info': {
            'full_name': repo_data.get('full_name', ''),
            'description': repo_data.get('description', ''),
            'html_url': repo_data.get('html_url', ''),
            'created_at': repo_data.get('created_at', ''),
            'updated_at': repo_data.get('updated_at', ''),
            'stargazers_count': repo_data.get('stargazers_count', 0),
        }
    }
    
    try:
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"[+] Saved report to: {report_filename}")
        return report_filename
    except Exception as e:
        print(f"[!] Error saving report: {str(e)}")
        return None


def send_credentials_telegram(project_name, credentials):
    """Send credentials information via Telegram"""
    if not ENABLE_TELEGRAM:
        return
    
    # Count findings
    total_findings = sum(len(v) for v in credentials.values())
    
    if total_findings == 0:
        return  # Don't send if no credentials found
    
    message = f"🔐 <b>Credentials Found</b>\n\n"
    message += f"🧅 <b>Hidden Service:</b> {HIDDEN_SERVICE_NAME}\n"
    message += f"📍 <b>Address:</b> {HIDDEN_SERVICE_ADDRESS}\n"
    message += f"📦 <b>Project:</b> {project_name}\n\n"
    
    if credentials['usernames']:
        message += f"👤 <b>Usernames ({len(credentials['usernames'])}):</b>\n"
        for username in credentials['usernames'][:5]:  # Limit to first 5
            message += f"  • {username}\n"
        if len(credentials['usernames']) > 5:
            message += f"  • ... and {len(credentials['usernames']) - 5} more\n"
        message += "\n"
    
    if credentials['passwords']:
        message += f"🔑 <b>Passwords ({len(credentials['passwords'])}):</b>\n"
        for password in credentials['passwords'][:5]:
            message += f"  • {password}\n"
        if len(credentials['passwords']) > 5:
            message += f"  • ... and {len(credentials['passwords']) - 5} more\n"
        message += "\n"
    
    if credentials['api_keys']:
        message += f"🔐 <b>API Keys ({len(credentials['api_keys'])}):</b>\n"
        for key in credentials['api_keys'][:3]:
            # Mask part of the key for security
            masked = key[:10] + "..." + key[-5:] if len(key) > 15 else key
            message += f"  • {masked}\n"
        if len(credentials['api_keys']) > 3:
            message += f"  • ... and {len(credentials['api_keys']) - 3} more\n"
        message += "\n"
    
    if credentials['tokens']:
        message += f"🎫 <b>Tokens ({len(credentials['tokens'])}):</b>\n"
        for token in credentials['tokens'][:3]:
            masked = token[:10] + "..." + token[-5:] if len(token) > 15 else token
            message += f"  • {masked}\n"
        if len(credentials['tokens']) > 3:
            message += f"  • ... and {len(credentials['tokens']) - 3} more\n"
        message += "\n"
    
    if credentials['emails']:
        message += f"📧 <b>Emails ({len(credentials['emails'])}):</b>\n"
        for email in credentials['emails'][:5]:
            message += f"  • {email}\n"
        if len(credentials['emails']) > 5:
            message += f"  • ... and {len(credentials['emails']) - 5} more\n"
    
    message += f"\n💾 Full report saved in reports directory"
    
    send_telegram_message(message)


def main():
    """Main execution function"""
    global success_count, error_count
    
    start_time = datetime.now()
    print(f"[*] Starting Community Kit data update at {start_time}")
    
    if ENABLE_TELEGRAM:
        send_telegram_message(
            f"🚀 <b>Community Kit Update Started</b>\n"
            f"Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Tor: {'Enabled' if USE_TOR else 'Disabled'}"
        )
    
    # Check if tracked_repos file exists
    if not os.path.exists(tracked_repos):
        error_msg = f"ERROR: {tracked_repos} file not found!"
        print(f"[!] {error_msg}")
        if ENABLE_TELEGRAM and NOTIFY_ON_ERROR:
            send_telegram_message(f"❌ <b>Error:</b> {error_msg}")
        sys.exit(1)
    
    # Walk through repo list
    with open(tracked_repos) as f:
        for repository in f.readlines():
            repository = repository.strip()
            if not repository or repository.startswith('#'):
                continue
            
            try:
                # Get Category and Project from line
                value = repository.split(",")
                if len(value) < 2:
                    print(f"[!] Skipping invalid line: {repository}")
                    continue
                
                category = value[0].strip()
                project = value[1].strip()
                
                # Get GitHub Repo JSON from API
                url = api_url_base + project
                print(f"[*] Processing: {project}")
                
                result = requests.get(url, headers=headers, proxies=proxies, timeout=30)
                
                if result.status_code == 200:
                    repo_data_json = json.loads(result.text)
                    
                    # Clone repos for further analysis
                    projectPath = "/tmp/" + project.replace('/', '_')
                    
                    # Clean up if directory already exists
                    if os.path.exists(projectPath):
                        import shutil
                        shutil.rmtree(projectPath)
                    
                    # Clone with error handling
                    try:
                        # Configure git to use proxy if Tor is enabled
                        if USE_TOR:
                            git_proxy = f"socks5h://{TOR_PROXY_HOST}:{TOR_PROXY_PORT}"
                            Repo.clone_from(
                                git_repo_base + project + ".git",
                                projectPath,
                                config=f'http.proxy={git_proxy}'
                            )
                        else:
                            Repo.clone_from(git_repo_base + project + ".git", projectPath)
                    except Exception as clone_error:
                        error_msg = f"Failed to clone {project}: {str(clone_error)}"
                        print(f"[!] {error_msg}")
                        error_messages.append(error_msg)
                        error_count += 1
                        continue
                    
                    # Determine if binaries exist in project
                    bins = contains_binary(projectPath)
                    print(f"    Binaries found: {len(bins)}")
                    
                    # Add custom has_binary field to JSON (FIXED BUG)
                    if not bins:
                        repo_data_json['has_binary'] = ""
                    else:
                        repo_data_json['has_binary'] = ", ".join(bins)
                    
                    # Get latest commit message and date
                    try:
                        current_repo = Repo(projectPath)
                        headcommit = current_repo.head.commit
                        commit_message = headcommit.message.strip()
                        commit_date = headcommit.committed_date
                        
                        repo_data_json['commit_message'] = commit_message
                        repo_data_json['commit_date'] = commit_date
                    except Exception as commit_error:
                        print(f"[!] Error getting commit info: {str(commit_error)}")
                        repo_data_json['commit_message'] = ""
                        repo_data_json['commit_date'] = 0
                    
                    # Add custom category field to JSON
                    repo_data_json['category'] = category
                    
                    # Extract credentials from repository
                    print(f"[*] Extracting credentials from {project}...")
                    credentials = extract_credentials(projectPath)
                    
                    # Save credentials report
                    report_file = save_credentials_report(project, credentials, repo_data_json)
                    
                    # Send Telegram notification if credentials found
                    send_credentials_telegram(project, credentials)
                    
                    # Add JSON to array
                    repo_data_json_text = json.dumps(repo_data_json)
                    repo_data.append(repo_data_json_text)
                    
                    success_count += 1
                    print(f"[+] Successfully processed: {project}")
                    
                else:
                    # FIXED BUG: use project instead of value
                    error_msg = f"ERROR: Can not access {project} (Status: {result.status_code})"
                    print(f"[!] {error_msg}")
                    error_messages.append(error_msg)
                    error_count += 1
                    
            except Exception as e:
                error_msg = f"ERROR processing {repository}: {str(e)}"
                print(f"[!] {error_msg}")
                error_messages.append(error_msg)
                error_count += 1
    
    # Build final JSON (data.json)
    data = ",".join(repo_data)
    data = jsonhead + data + jsonfoot
    
    try:
        with open(datajson, 'w') as f:
            f.write(data)
        print(f"\n[+] Data written to {datajson}")
    except Exception as e:
        error_msg = f"ERROR writing to {datajson}: {str(e)}"
        print(f"[!] {error_msg}")
        error_messages.append(error_msg)
        error_count += 1
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    summary = f"""
╔════════════════════════════════════════╗
║     Community Kit Update Summary       ║
╠════════════════════════════════════════╣
║ Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}      ║
║ End Time:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}      ║
║ Duration:   {duration:.2f} seconds              ║
║ Success:    {success_count} repositories            ║
║ Errors:     {error_count} repositories            ║
╚════════════════════════════════════════╝
"""
    print(summary)
    
    # Send Telegram notification
    if ENABLE_TELEGRAM:
        if success_count > 0 and NOTIFY_ON_SUCCESS:
            telegram_summary = (
                f"✅ <b>Community Kit Update Complete</b>\n\n"
                f"⏱ Duration: {duration:.1f}s\n"
                f"✅ Success: {success_count}\n"
                f"❌ Errors: {error_count}\n"
                f"🌐 Tor: {'Enabled' if USE_TOR else 'Disabled'}"
            )
            
            if error_messages and NOTIFY_ON_ERROR:
                telegram_summary += f"\n\n<b>Errors:</b>\n"
                for error in error_messages[:5]:  # Show first 5 errors
                    telegram_summary += f"• {error}\n"
                if len(error_messages) > 5:
                    telegram_summary += f"• ... and {len(error_messages) - 5} more"
            
            send_telegram_message(telegram_summary)
        elif error_count > 0 and NOTIFY_ON_ERROR:
            telegram_summary = (
                f"❌ <b>Community Kit Update Failed</b>\n\n"
                f"❌ Errors: {error_count}\n"
                f"First error: {error_messages[0] if error_messages else 'Unknown'}"
            )
            send_telegram_message(telegram_summary)
    
    # Exit with error code if there were errors
    if error_count > 0:
        sys.exit(1)
    
    print("\n[+] Update completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Update interrupted by user")
        if ENABLE_TELEGRAM and NOTIFY_ON_ERROR:
            send_telegram_message("⚠️ <b>Community Kit Update Interrupted</b>\nUpdate was stopped by user")
        sys.exit(1)
    except Exception as e:
        error_msg = f"FATAL ERROR: {str(e)}"
        print(f"\n[!] {error_msg}")
        if ENABLE_TELEGRAM and NOTIFY_ON_ERROR:
            send_telegram_message(f"💥 <b>Fatal Error</b>\n{error_msg}")
        sys.exit(1)
