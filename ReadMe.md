# BoringBot v2.1 - The Solo Miner's Companion 🚀

A high-performance, modular Telegram suite designed for the serious solo miner. BoringBot monitors CKPool solo mining performance, local ADS-B airspace traffic, and server telemetry in a single unified interface.

## 🛠 New in v2.1
* **Auto-Discovery Engine:** Automatically detects active miners via log timestamps. No more manual `MINER_ID` or `WORKER_ID` entries in the config.
* **100k Line Deep Scan:** Robust parsing that eliminates "0T" (Zero Terahash) errors by scanning deeper into CKPool log rotations.
* **Pool Merge Logic:** Seamlessly combines hashrate and Shares Per Second (SPS) across multiple miners into a single "Total Performance" view.
* **Active Airspace Monitor:** A dedicated background thread scans local ADS-B feeds every 10s with built-in 15-minute alert cooldowns to prevent notification fatigue.
* **Enhanced Resilience:** Comprehensive `try-except` blocks protect the bot from crashing during network blips or pool disconnects.

## 📦 Project Modules
* `boring_bot.py`: The Launcher. Manages threading and registers Telegram handlers.
* `boring_stats.py`: The Core Engine. Handles log parsing and miner auto-discovery.
* `boring_adsb.py`: Airspace Monitor. Tracks proximity aircraft via `dump1090/readsb`.
* `boring_menu.py`: The UI. Manages the Telegram Menu Button and `/help` command.
* `boring_system.py` & `boring_economics.py`: Calculations for server health and mining profitability.

## 🚀 Installation & Setup
1.  **Clone & Clean:** Ensure you are in your deployment directory.
2.  **Install Dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```
3.  **Configuration:**
    Copy `boring_config.example.py` to `boring_config.py` and update:
    * `TOKEN`: Your Telegram Bot Token.
    * `CHAT_ID`: Your Telegram User ID.
    * `LOG_FILE`: Path to your CKPool log file.
    * `ADSB_URL`: URL to your `aircraft.json` (usually port 8080).

## ⚙️ Running as a Daemon (Systemd)
To ensure BoringBot runs 24/7 and restarts on failure:
1.  **Create the service file:**
    `sudo nano /etc/systemd/system/boring_bot.service`
2.  **Paste the configuration:**
    ```ini
    [Unit]
    Description=BoringBot v2.1 Service
    After=network.target

    [Service]
    Type=simple
    User=homelab
    WorkingDirectory=/home/homelab/BoringBot-Release
    ExecStart=/usr/bin/python3 boring_bot.py
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    ```
3.  **Enable and Start:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable boring_bot.service
    sudo systemctl start boring_bot.service
    ```
