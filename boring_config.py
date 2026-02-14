import os

# ==========================================
#         BORING-SERVER CONFIGURATION
# ==========================================

# --- SECRETS ---
TOKEN = 'TOKEN:ID'
CHAT_ID = 'CHATID'

# --- SYSTEM PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to CKPool Log
# Updated to LOG_FILE_PATH for the new stats engine
LOG_FILE_PATH = "/home/homelab/ckpool/logs/ckpool.log"
LOG_FILE = LOG_FILE_PATH  # Alias kept for backward compatibility

# Path to ADS-B JSON (readsb or dump1090-fa)
ADSB_FILE = "/run/readsb/aircraft.json"

# Path to CPU Temperature Sensor
TEMP_SENSOR = "/sys/class/thermal/thermal_zone0/temp"

# --- MINING IDENTIFIERS ---
# The main wallet string to search for in logs
MINER_ID = 'bc1q4u73smyy7vefny2mtjmkkjn6z6s2pgmsflmq4d'

# Specific Worker IDs for the Menu System
# These MUST match the "Authorized client" lines in your log exactly
WORKER_1_ID = "User bc1q4u73smyy7vefny2mtjmkkjn6z6s2pgmsflmq4d :"
WORKER_2_ID = "User bc1q4u73smyy7vefny2mtjmkkjn6z6s2pgmsflmq4d:"
EXPECTED_WORKERS = 2

# boring_config.py (Snippet to Add)
WORKER_COUNT = 2
# Optionally add worker suffixes if you want to filter or label exactly
WORKER1_SUFFIX = "heater1"
WORKER2_SUFFIX = "heater2"

# High Score Files (Stored in the bot directory)
# We now track separate high scores for the Pool and each Miner
BEST_SHARE_FILE = os.path.join(BASE_DIR, 'best_share.txt') # Legacy
ATH_FILE_POOL   = os.path.join(BASE_DIR, 'ath_pool.txt')
ATH_FILE_M1     = os.path.join(BASE_DIR, 'ath_miner1.txt')
ATH_FILE_M2     = os.path.join(BASE_DIR, 'ath_miner2.txt')

# --- MINING SETTINGS ---
DEFAULT_HASHRATE = 95.0       # Used for estimates if logs are silent (TH/s)
MIN_HASHRATE = 80.0           # Alert if TOTAL Pool Hashrate drops below this (TH/s)
TOTAL_WATTS = 3050            # S19 XP/Pro wattage
KWH_PRICE = 0.14              # Electricity rate in $/kWh
DEFAULT_DIFFICULTY = 125864590119494.0 # Fallback Difficulty

# --- LOCATION SETTINGS ---
HOME_LAT = 80.1109
HOME_LON = -20.2375
ALERT_RADIUS = 4.0            # Alert if plane is closer than X miles

# --- API SETTINGS ---
USER_AGENT = 'Mozilla/5.0 (Boring-Server/1.0)'
MEMPOOL_API = "https://mempool.space/api/v1"
