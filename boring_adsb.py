import json
import math
import os
import time
import threading
import boring_config

# --- ALERT CACHE ---
# Prevents spamming the same alert every 10 seconds.
# We store 'HEXCODE': timestamp_of_last_alert
alerted_planes = {}

def haversine(lat1, lon1, lat2, lon2):
    """ Calculates distance in Miles between two GPS coordinates. """
    R = 3958.8 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_aircraft_data():
    """ Safely reads the ADS-B JSON file. """
    if not os.path.exists(boring_config.ADSB_FILE):
        return []
    try:
        with open(boring_config.ADSB_FILE, 'r') as f:
            data = json.load(f)
            return data.get('aircraft', [])
    except:
        return []

# ==========================================
# 1. BACKGROUND THREAD (The Alert System)
# ==========================================

def start_adsb_monitor(bot):
    def monitor_loop():
        print("✈️ ADS-B Monitor Started...")
        
        while True:
            try:
                planes = get_aircraft_data()
                current_time = time.time()
                
                # 1. Clean up old alerts (Clear cache every 15 mins)
                # If a plane leaves and comes back later, we want to alert again.
                expired = [k for k, v in alerted_planes.items() if (current_time - v) > 900]
                for k in expired: del alerted_planes[k]

                # 2. Check for Proximity
                for p in planes:
                    # Skip invalid data
                    if 'lat' not in p or 'lon' not in p: continue
                    
                    dist = haversine(boring_config.HOME_LAT, boring_config.HOME_LON, p['lat'], p['lon'])
                    
                    # ALERT CONDITION: Plane is closer than Config Radius (4.0 mi)
                    if dist <= boring_config.ALERT_RADIUS:
                        hex_code = p.get('hex', 'unknown')
                        
                        # Only alert if we haven't alerted this plane recently
                        if hex_code not in alerted_planes:
                            
                            flight = p.get('flight', 'N/A').strip()
                            if not flight: flight = f"Unk ({hex_code})"
                            
                            alt = p.get('alt_baro', 'GND')
                            if alt == "ground": alt = 0
                            
                            msg = (f"🚨 *AIRSPACE ALERT* 🚨\n"
                                   f"Plane Detected within {boring_config.ALERT_RADIUS} miles!\n"
                                   f"━━━━━━━━━━━━━━\n"
                                   f"✈️ *{flight}*\n"
                                   f"📏 *Dist:* {dist:.1f} mi\n"
                                   f"🏔️ *Alt:* {alt} ft")
                            
                            print(f"⚠️ Sending Alert for {flight} ({dist:.1f}mi)")
                            bot.send_message(boring_config.CHAT_ID, msg, parse_mode='Markdown')
                            
                            # Add to ignore list for 15 mins
                            alerted_planes[hex_code] = current_time

            except Exception as e:
                print(f"❌ Air Monitor Error: {e}")
            
            # Scan every 10 seconds
            time.sleep(10)

    # Start the thread safely
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()

# ==========================================
# 2. HANDLERS (The Commands)
# ==========================================

def register_handlers(bot):
    
    @bot.message_handler(commands=['planes', 'air'])
    def handle_planes(message):
        try:
            if str(message.chat.id) != boring_config.CHAT_ID: return
            
            planes = get_aircraft_data()
            if not planes:
                bot.reply_to(message, "❌ No aircraft detected (or file missing).")
                return

            # Calculate distances
            nearby = []
            for p in planes:
                if 'lat' in p and 'lon' in p:
                    dist = haversine(boring_config.HOME_LAT, boring_config.HOME_LON, p['lat'], p['lon'])
                    
                    hex_code = p.get('hex', 'Unknown')
                    flight = p.get('flight', 'N/A').strip()
                    if not flight: flight = f"Unk ({hex_code})"
                    
                    alt = p.get('alt_baro', 'GND')
                    
                    nearby.append({'dist': dist, 'id': flight, 'alt': alt})

            # Sort by closest first
            nearby.sort(key=lambda x: x['dist'])
            
            # Build Report
            msg = f"✈️ *Airspace Report (Top 5)*\n"
            if not nearby: msg += "No aircraft detected."
            
            for p in nearby[:5]:
                msg += f"• *{p['id']}*: {p['dist']:.1f}mi away @ {p['alt']}ft\n"
                
            bot.reply_to(message, msg, parse_mode='Markdown')
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {e}")
