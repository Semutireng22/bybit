# ByBit Game Bot

## Description
ByBit Game Bot is an automated bot designed to interact with the ByBit platform, playing games and managing scores. The bot features random win/lose functionality, and it can be configured to always win based on user preferences.

## Features
- Allows configuration for always winning.
- Multi accounts

## Installation Guide

### Clone the Repository
To get started, clone the repository from GitHub:

```bash
git clone https://github.com/Semutireng22/bybit
```

### Open the Folder
Navigate into the cloned project directory:

```bash
cd bybit
```

### Install Requirements
Install the required Python packages using pip. You can do this by running:

```bash
pip install -r requirements.txt
```

## Configuration
Before running the bot, make sure to edit the following files:

1. **`data.txt`**: This file should contain your login credentials or initialization data for ByBit.
   - Each line should represent a separate initialization data entry.
     Example :
     ` query_id=xxxxxxxxxxx` or `user=xxxxxxxxxxxxxx`

2. **`config.json`**: This file contains configuration settings for the bot.
   - Example :
     ```json
     {
         "always_win": false
     }
     ```

## Running the Program
To start the bot, run the following command:

```bash
python3 bybit.py
```

## Additional Notes
- Ensure you have Python installed on your machine. The bot is compatible with Python 3.x.
- Modify the `always_win` setting in `config.json` to `true` if you want the bot to always win.
