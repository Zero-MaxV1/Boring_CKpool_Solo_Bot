import subprocess
import json
import os
import time
import threading
import requests
import datetime
import boring_config
import telebot

# ==========================================
# 1. SMART LOG PARSER
# ==========================================

def parse_log_time(line):
    """ Extracts timestamp [2026-02-14 07:47:38] from log line. """
    try:
        # Assumes format: [YYYY-MM-DD HH:MM:SS.ms]
        if line.startswith('['):
            ts_str = line[1:20] # Grab just the date/time part
            dt = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            return dt.timestamp()
    except: pass
    return 0

def get_merged_pool_stats():
    """ Merges Pool hashrate and SPS lines. """
    log_path = getattr(boring_config, 'LOG_FILE_PATH', getattr(boring_config, 'LOG_FILE', ''))
    if not os.path.exists(log_path): return None
    
    stats = {}
    try:
        cmd = f"tail -n 5000 {log_path}"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore').strip()
        lines = output.split('\n')
        
        found_hash = False
        found_sps = False
        last_ts = 0
        
        for line in reversed(lines):
            ts = parse_log_time(line)
            if ts > last_ts: last_ts = ts
            
            if "Pool:{" in line:
                try:
                    json_part = "{" + line.split('Pool:{', 1)[1].strip()
                    data = json.loads(json_part)
                    
                    if "hashrate1m" in data and not found_hash:
                        stats.update(data)
                        found_hash = True
                    if "SPS1m" in data and not found_sps:
                        stats.update(data)
                        found_sps = True
                except: continue
        
        if stats:
            stats['_last_seen'] = last_ts
            return stats
    except: return None
    return None

def get_active_miners():
    """
    Finds the 2 most recent active miners based on Log Timestamps.
    """
    log_path = getattr(boring_config, 'LOG_FILE_PATH', getattr(boring_config, 'LOG_FILE', ''))
    miners_list = []
    
    try:
        # Scan deep (50k lines) to find real mining data amidst spam
        cmd = f"tail -n 50000 {log_path} | grep 'User '"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore').strip()
        lines = output.split('\n')
        
        unique_sigs = {}
        
        for line in lines:
            if "{" in line:
                try:
                    # Parse Timestamp
                    ts = parse_log_time(line)
                    
                    # Parse Data
                    parts = line.split('{')
                    signature = parts[0].strip()
                    json_part = "{" + parts[1].strip()
                    data = json.loads(json_part)
                    
                    # Filter: Must have valid 1m or 5m hashrate
                    h1 = data.get('hashrate1m', '0').replace('T','').replace('M','')
                    if float(h1) > 0:
                        data['_id'] = signature
                        data['_last_seen'] = ts
                        # Keep only the NEWEST entry for this signature
                        unique_sigs[signature] = data
                except: continue
        
        # Convert to list
        all_miners = list(unique_sigs.values())
        
        # Sort by Time (Newest First)
        all_miners.sort(key=lambda x: x.get('_last_seen', 0), reverse=True)
        
        # Take top 2
        return all_miners[:2]
    except: return []

# ==========================================
# 2. DATA UTILITIES
# ==========================================

def update_ath(current_score, filename):
    if not current_score: return 0
    try: current_score = float(current_score)
    except: return 0
        
    file_best = 0.0
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
                if content: file_best = float(content)
        except: pass

    if current_score > file_best:
        try:
            with open(filename, 'w') as f: f.write(f"{current_score:.0f}")
            return current_score
        except: return file_best
    return file_best

def get_network_stats():
    price = 0; net_diff = 0
    headers = {'User-Agent': 'BoringBot/2.0'}
    try:
        r = requests.get(f"{boring_config.MEMPOOL_API}/prices", headers=headers, timeout=5)
        price = float(r.json()['USD'])
    except: pass
    try:
        r = requests.get(f"{boring_config.MEMPOOL_API}/mining/difficulty-adjustment", headers=headers, timeout=5)
        net_diff = float(r.json()['difficulty'])
    except:
        if net_diff == 0: net_diff = 125864590119494.0
    return price, net_diff

# ==========================================
# 3. REPORT GENERATOR
# ==========================================

def generate_report(data, label, ath_file):
    if not data: return f"❌ *{label}*: Data not found."
    
    price, net_diff = get_network_stats()
    
    def clean(val):
        if not val: return "0T"
        return str(val).replace('M', ' M').replace('G', ' G').replace('T', ' T').replace('P', ' P')

    h1m  = clean(data.get('hashrate1m', '0T'))
    h5m  = clean(data.get('hashrate5m', '0T'))
    h15m = clean(data.get('hashrate15m', '0T'))
    h1h  = clean(data.get('hashrate1hr', '0T'))
    h1d  = clean(data.get('hashrate1d', '0T'))
    
    session_best = data.get('bestshare', 0)
    if not session_best: session_best = data.get('bestever', 0)
    
    # Calculate Time Ago using Log Timestamp
    last_ts = data.get('_last_seen', 0)
    ago_str = "Unknown"
    if last_ts > 0:
        diff = int(time.time()) - int(last_ts)
        if diff < 60: ago_str = f"{diff}s ago"
        elif diff < 3600: ago_str = f"{diff//60}m ago"
        else: ago_str = f"{diff//3600}h ago"

    sps_section = ""
    sps = data.get('SPS1m', 0)
    if sps: sps_section = f"📈 *SPS (1m):* `{sps}`\n"

    all_time_best = update_ath(session_best, ath_file)

    try:
        progress = (float(session_best) / net_diff) * 100
        luck_denom = net_diff / float(session_best) if float(session_best) > 0 else 0
        luck_str = f"1 in {luck_denom/1e6:.1f}M" if luck_denom > 1e6 else f"1 in {int(luck_denom):,}"
    except:
        progress = 0; luck_str = "N/A"

    usd_val = 3.125 * price

    return (f"🏭 *{label} STATUS*\n"
            f"━━━━━━━━━━━━━━\n"
            f"⚡ *1m:* `{h1m}`  |  ⚡ *5m:* `{h5m}`\n"
            f"⚡ *15m:* `{h15m}` |  ⚡ *1h:* `{h1h}`\n"
            f"📅 *24h Avg:* `{h1d}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"{sps_section}"
            f"⏱️ *Last Activity:* {ago_str}\n"
            f"🏆 *Session Best:* `{int(session_best):,}`\n"
            f"🌟 *All-Time Best:* `{int(all_time_best):,}`\n"
            f"🎲 *Luck:* {luck_str}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 *BTC Price:* `${price:,.0f}`\n"
            f"💵 *Pot Value:* `${usd_val:,.0f}`")

# ==========================================
# 4. BACKGROUND THREADS
# ==========================================

def start_threads(bot):
    def jackpot_monitor():
        log_path = getattr(boring_config, 'LOG_FILE_PATH', getattr(boring_config, 'LOG_FILE', ''))
        try:
            with open(log_path, 'r') as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if not line: time.sleep(1); continue
                    if "Solved block" in line:
                        bot.send_message(boring_config.CHAT_ID, f"🎉 JACKPOT!!!\n{line.strip()}")
        except: pass

    def health_monitor():
        last_alert = 0
        while True:
            try:
                pool = get_merged_pool_stats()
                if pool:
                    raw = pool.get('hashrate5m', '0T').replace('T','').replace('P','000').replace('G','0.001')
                    try:
                        val = float(raw)
                        if val < boring_config.MIN_HASHRATE:
                            if (time.time() - last_alert) > 3600:
                                bot.send_message(boring_config.CHAT_ID, f"⚠️ Low Hashrate: {val}T")
                                last_alert = time.time()
                    except: pass
            except: pass
            time.sleep(60)

    threading.Thread(target=jackpot_monitor, daemon=True).start()
    threading.Thread(target=health_monitor, daemon=True).start()

# ==========================================
# 5. HANDLERS
# ==========================================

def register_handlers(bot):

    @bot.message_handler(commands=['stats', 'fleet'])
    def handle_stats(message):
        try:
            if str(message.chat.id) != boring_config.CHAT_ID: return
            
            pool_data = get_merged_pool_stats()
            miners = get_active_miners()
            
            def get_sum(m):
                if not m: return "OFFLINE"
                h = m.get('hashrate5m', '0T')
                if h == '0T' or h == '0': h = m.get('hashrate1m', '0T')
                return str(h).replace('M',' M').replace('G',' G').replace('T',' T')

            m1 = miners[0] if len(miners) > 0 else None
            m2 = miners[1] if len(miners) > 1 else None

            msg = "🎛️ *FLEET COMMAND*\n"
            msg += "━━━━━━━━━━━━━━\n"
            msg += f"🔥 *Heater 1:* `{get_sum(m1)}`\n"
            msg += f"🔥 *Heater 2:* `{get_sum(m2)}`\n"
            msg += "━━━━━━━━━━━━━━\n"
            
            ath_file = getattr(boring_config, 'ATH_FILE_POOL', 'ath_pool.txt')
            report = generate_report(pool_data, "TOTAL SYSTEM", ath_file)
            msg += report.split("━━━━━━━━━━━━━━\n", 1)[1] 
            
            bot.reply_to(message, msg, parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {e}")

    @bot.message_handler(commands=['miner1'])
    def handle_miner1(message):
        try:
            if str(message.chat.id) != boring_config.CHAT_ID: return
            miners = get_active_miners()
            data = miners[0] if len(miners) > 0 else None
            ath_file = getattr(boring_config, 'ATH_FILE_M1', 'ath_miner1.txt')
            msg = generate_report(data, "HEATER 1", ath_file)
            bot.reply_to(message, msg, parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {e}")

    @bot.message_handler(commands=['miner2'])
    def handle_miner2(message):
        try:
            if str(message.chat.id) != boring_config.CHAT_ID: return
            miners = get_active_miners()
            data = miners[1] if len(miners) > 1 else None
            ath_file = getattr(boring_config, 'ATH_FILE_M2', 'ath_miner2.txt')
            msg = generate_report(data, "HEATER 2", ath_file)
            bot.reply_to(message, msg, parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {e}")
