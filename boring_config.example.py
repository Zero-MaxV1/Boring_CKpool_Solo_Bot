import os

# ==========================================
#   BORING-SERVER CONFIGURATION (EXAMPLE)
# ==========================================

# --- SECRETS (REQUIRED) ---
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'
CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID_HERE'

# --- SYSTEM PATHS ---
# Update these paths to match your local setup
# Note: LOG_FILE_PATH must point to your cgminer/ckpool log
LOG_FILE_PATH = "/home/homelab/ckpool/logs/ckpool.log"
ADSB_FILE = "/run/readsb/aircraft.json"
TEMP_SENSOR = "/sys/class/thermal/thermal_zone0/temp"

# --- MINING SETTINGS ---
# Your Bitcoin Wallet Address (Used for tracking)
MINER_ID = 'YOUR_BTC_WALLET_ADDRESS'

# Alert Settings
EXPECTED_WORKERS = 2   # Set to 1 if you only have one miner
MIN_HASHRATE = 80.0    # Alert threshold (TH/s)

# --- ECONOMICS ---
TOTAL_WATTS = 3050     # Total power draw (Watts)
KWH_PRICE = 0.14       # Your electricity cost ($/kWh)

# --- LOCATION (FOR ADS-B ALERTS) ---
# Set to your home coordinates (Decimal Degrees)
HOME_LAT = 0.0000
HOME_LON = 0.0000
ALERT_RADIUS = 4.0     # Miles

# --- INTERNAL PATHS (DO NOT CHANGE) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATH_FILE_POOL = os.path.join(BASE_DIR, 'ath_pool.txt')
ATH_FILE_M1   = os.path.join(BASE_DIR, 'ath_miner1.txt')
ATH_FILE_M2   = os.path.join(BASE_DIR, 'ath_miner2.txt')

# --- API ENDPOINTS ---
MEMPOOL_API = "https://mempool.space/api/v1"
