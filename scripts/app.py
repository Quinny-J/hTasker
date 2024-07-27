import os
import subprocess
import requests
from github import Github
from datetime import datetime

# Constants
#GITHUB_TOKEN = "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"
GITHUB_TOKEN = "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"
REPO_NAME = "Quinny-J/gitStreaker"
CONFIG_FILE = "config.txt"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1261261591400153099/vrgvZBVkkgCpgwbmMLB6jumpt1g7X3X3kSxX2s7hwV-Lx6Qfjzyg6BZxWDopsIepuKGO"

# Get the current directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = SCRIPT_DIR  # Use the current directory as the repository path

# Change directory to the local repository
os.chdir(REPO_PATH)

# Verify that 'origin' is set correctly
#subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{REPO_NAME}.git"], check=True)

# Read current count of days from config file
config_file_path = os.path.join(REPO_PATH, CONFIG_FILE)
with open(config_file_path, 'r') as f:
    days_count = int(f.read().strip())

# Increment the days count
days_count += 1

# Update config file with new count
with open(config_file_path, 'w') as f:
    f.write(str(days_count))

# Commit message
COMMIT_MESSAGE = f"Daily commit: Day {days_count}"

# Stage all changes
subprocess.run(["git", "add", "."], check=True)

# Commit changes
subprocess.run(["git", "commit", "-m", COMMIT_MESSAGE], check=True)

# Push changes to GitHub
subprocess.run(["git", "push", "origin", "main"], check=True)

# Send message to Discord webhook
discord_message = f"Script has been executed. Day {days_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
payload = {
    "content": discord_message
}
headers = {
    "Content-Type": "application/json"
}
response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)

if response.status_code == 204:
    print("Discord webhook notification sent successfully.")
else:
    print(f"Failed to send Discord webhook notification. Status code: {response.status_code}")

# If you want to use the GitHub API for additional actions:
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)