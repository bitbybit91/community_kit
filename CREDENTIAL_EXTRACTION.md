# Credential Extraction and Reporting

## Overview

The VPS edition now includes automatic credential extraction and reporting functionality. The script scans all cloned repositories for potential sensitive information and reports findings via Telegram and local JSON files.

## Features

### 1. Automatic Credential Detection

The script searches for the following types of sensitive information:

- **Usernames**: Common username patterns in configuration files
- **Passwords**: Password fields and values
- **API Keys**: API key patterns and configurations
- **Tokens**: Access tokens, auth tokens, bearer tokens
- **Emails**: Email addresses
- **URLs**: Connection strings and endpoints

### 2. Report Storage

All findings are stored in the `reports/` directory inside the main project:

```
community_kit/
├── reports/
│   ├── owner_project_report.json
│   ├── another_owner_project_report.json
│   └── ...
```

Each report contains:
- Timestamp of analysis
- Hidden service information (address and name)
- Project details (name, description, URL)
- Extracted credentials by category
- Repository metadata

### 3. Telegram Notifications

When credentials are found, a formatted message is sent via Telegram containing:

- 🧅 **Hidden Service Name**: Identifies which service found the data
- 📍 **Hidden Service Address**: The .onion address
- 📦 **Project Name**: Repository that contained credentials
- 👤 **Usernames**: List of found usernames (first 5)
- 🔑 **Passwords**: List of found passwords (first 5)
- 🔐 **API Keys**: Masked API keys (first 3)
- 🎫 **Tokens**: Masked tokens (first 3)
- 📧 **Emails**: List of email addresses (first 5)

## Configuration

Add the following to your `config.env` file:

```bash
# Hidden Service Configuration
HIDDEN_SERVICE_ADDRESS=your_hidden_service.onion
HIDDEN_SERVICE_NAME=my_hidden_service
```

These values will be included in all reports and Telegram notifications to identify the source of the findings.

## Report Format

Each JSON report has the following structure:

```json
{
  "timestamp": "2025-11-13T12:00:00.000000",
  "hidden_service": "example.onion",
  "hidden_service_name": "main_scanner",
  "project": "owner/repository",
  "credentials": {
    "usernames": ["admin", "user1"],
    "passwords": ["pass123", "secret"],
    "api_keys": ["sk_live_abc123..."],
    "tokens": ["ghp_xyz789..."],
    "emails": ["admin@example.com"],
    "other_sensitive": []
  },
  "repository_info": {
    "full_name": "owner/repository",
    "description": "Repository description",
    "html_url": "https://github.com/owner/repository",
    "created_at": "2020-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "stargazers_count": 100
  }
}
```

## Telegram Message Example

```
🔐 Credentials Found

🧅 Hidden Service: main_scanner
📍 Address: example.onion
📦 Project: owner/repository

👤 Usernames (2):
  • admin
  • developer

🔑 Passwords (3):
  • MyPassword123
  • SecurePass!
  • temp_password

🔐 API Keys (1):
  • sk_live_abc...xyz

📧 Emails (2):
  • admin@example.com
  • contact@example.com

💾 Full report saved in reports directory
```

## Security Considerations

### 1. Report Protection

The `reports/` directory is automatically added to `.gitignore` to prevent accidentally committing sensitive data.

### 2. Sensitive Data Masking

In Telegram notifications:
- API keys and tokens are partially masked (showing only first 10 and last 5 characters)
- Only the first few items of each category are shown to prevent message overflow
- Full details are available in the JSON reports

### 3. Pattern Filtering

The extraction engine filters out common false positives:
- Example values ("example", "test", "your_")
- Placeholder values ("xxx", "***")
- Generic credentials ("admin", "root", "user", "password")

These filters reduce noise but may miss some valid credentials. Review reports carefully.

## File Types Scanned

The following file types are scanned for credentials:

- Configuration: `.conf`, `.config`, `.ini`, `.env`, `.yml`, `.yaml`, `.json`, `.xml`, `.properties`
- Scripts: `.sh`, `.bat`, `.ps1`, `.py`, `.js`, `.php`, `.rb`, `.go`
- Source code: `.java`, `.c`, `.cpp`, `.cs`
- Text files: `.txt`

Binary files and `.git` directories are automatically skipped.

## Usage

The credential extraction runs automatically when using `get_repo_data_vps.py`:

```bash
# Set up configuration
cp config.env.example config.env
nano config.env  # Add your tokens and hidden service info

# Run the scanner
python3 get_repo_data_vps.py
```

The script will:
1. Clone each repository
2. Scan for credentials
3. Save report to `reports/` directory
4. Send Telegram notification if credentials found
5. Continue with normal processing

## Viewing Reports

### List all reports
```bash
ls -lh reports/
```

### View a specific report
```bash
cat reports/owner_project_report.json | python3 -m json.tool
```

### Search for specific credentials
```bash
# Find all passwords
grep -r "passwords" reports/ | grep -v "\[\]"

# Find all API keys
grep -r "api_keys" reports/ | grep -v "\[\]"
```

## Troubleshooting

### No credentials found

If no credentials are detected:
1. Check that repositories contain searchable files (not just binaries)
2. Verify file extensions are in the searchable list
3. Review pattern filters - they may be too strict
4. Check that files contain actual credential patterns

### Telegram not sending

If credentials are found but Telegram doesn't notify:
1. Verify `ENABLE_TELEGRAM_NOTIFICATIONS=true` in config.env
2. Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct
3. Ensure bot has permission to send messages to the chat
4. Check network connectivity (especially if using Tor)

### Reports directory not created

The script automatically creates the `reports/` directory on startup. If it doesn't exist:
```bash
mkdir -p reports
chmod 755 reports
```

## Privacy and Legal Considerations

⚠️ **Important**: This tool is designed for security research and authorized testing only.

- Only scan repositories you have permission to analyze
- Respect privacy and data protection laws
- Secure the `reports/` directory appropriately
- Use Tor for anonymity when appropriate
- Don't share extracted credentials publicly
- Follow responsible disclosure practices

## Advanced Configuration

### Custom Patterns

To add custom credential patterns, edit the `extract_credentials()` function in `get_repo_data_vps.py` and add to the `patterns` dictionary.

### Exclude Patterns

To exclude certain patterns from reports, add them to the filter list at the end of `extract_credentials()`:

```python
credentials[key] = [item for item in credentials[key] if item.lower() not in 
                   ['example', 'test', 'your_custom_filter']]
```

### Report Retention

Reports are never automatically deleted. To clean up old reports:

```bash
# Delete reports older than 30 days
find reports/ -name "*.json" -mtime +30 -delete

# Archive old reports
tar -czf reports_backup_$(date +%Y%m%d).tar.gz reports/
```

## Performance

Credential extraction adds minimal overhead:
- ~1-2 seconds per repository
- Scales linearly with repository size
- Most time spent on file I/O and pattern matching
- No impact on network operations

For large-scale operations, consider:
- Running during off-peak hours
- Using faster storage for the reports directory
- Filtering repositories by size or type
