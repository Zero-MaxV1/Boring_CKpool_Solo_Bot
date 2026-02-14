# BoringBot - The Solo Miner's Companion

A modular Telegram bot for tracking CKPool solo mining, local ADS-B aircraft traffic, and server health.

## Features
- ⛏️ Real-time Mining Stats (Hashrate, Luck, Difficulty)
- 💸 Economics Calculator (Electricity Cost vs. Jackpot Odds)
- ✈️ Local Airspace Radar (reads dump1090/readsb JSON)
- ❤️ Server Health Monitoring (Temp, RAM, Public IP)
- 🔔 Auto-alert on Hashrate Drop or Fleet Silence

## Installation
1. Install Python 3 and Pip:
   sudo apt install python3-pip

2. Install Dependencies:
   pip3 install -r requirements.txt

3. Configuration:
   Edit 'boring_config.py' with your settings:
   - TOKEN: Your Telegram Bot Token
   - CHAT_ID: Your User ID
   - LOG_FILE: Path to your ckpool log
   - MINER_ID: Your BTC address or worker name

4. Run it:
   python3 boring_bot.py

## Auto-Start (Systemd)
Copy the service file to /etc/systemd/system/boring_bot.service and enable it.
