import subprocess
import os
import socket
import requests  # <--- NEW IMPORT
import boring_config

def get_cpu_temp():
    """Reads the thermal zone to get CPU temp."""
    try:
        with open(boring_config.TEMP_SENSOR, "r") as f:
            temp = float(f.read()) / 1000.0
        return f"{temp:.1f}°C"
    except:
        return "N/A"

def get_public_ip():
    """Asks an external server for our WAN IP."""
    try:
        # Timeout is fast (3s) so the bot doesn't hang if internet is slow
        return requests.get("https://api.ipify.org", timeout=3).text
    except:
        return "Unknown"

def get_system_stats():
    """Gathers all vital server statistics."""
    stats = {}
    
    # 1. Uptime
    try:
        stats['uptime'] = subprocess.check_output("uptime -p", shell=True).decode().strip().replace("up ", "")
    except: stats['uptime'] = "Unknown"

    # 2. Disk Usage (Root Partition)
    try:
        df = subprocess.check_output("df -h /", shell=True).decode().split('\n')[1].split()
        stats['disk_used'] = df[2]
        stats['disk_total'] = df[1]
        stats['disk_pct'] = df[4]
    except: stats['disk_pct'] = "N/A"

    # 3. RAM Usage
    try:
        free = subprocess.check_output("free -m", shell=True).decode().split('\n')[1].split()
        total_mem = int(free[1])
        used_mem = int(free[2])
        stats['ram_pct'] = int((used_mem / total_mem) * 100)
        stats['ram_usage'] = f"{used_mem}MB / {total_mem}MB"
    except: stats['ram_pct'] = 0

    # 4. CPU Load & Temp
    stats['load'] = os.getloadavg()[0]
    stats['temp'] = get_cpu_temp()

    # 5. Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        stats['local_ip'] = s.getsockname()[0]
        s.close()
    except: stats['local_ip'] = "127.0.0.1"

    # 6. Public IP (NEW)
    stats['public_ip'] = get_public_ip()

    return stats

# --- PLUGIN REGISTRATION ---
def register_handlers(bot):
    @bot.message_handler(commands=['health'])
    def handle_health(message):
        if str(message.chat.id) == boring_config.CHAT_ID:
            s = get_system_stats()
            
            # Health Status Icon
            status_icon = "🟢"
            if s['load'] > 2.0 or s['ram_pct'] > 90: status_icon = "⚠️"
            if "N/A" not in s['temp'] and float(s['temp'].replace("°C","")) > 75: status_icon = "🔥"

            msg = (f"{status_icon} *Boring-Server Status*\n"
                   f"━━━━━━━━━━━━━━\n"
                   f"🌡️ *Temp:* {s['temp']}\n"
                   f"🧠 *RAM:* {s['ram_pct']}% ({s['ram_usage']})\n"
                   f"💾 *Disk:* {s['disk_pct']} Full ({s['disk_used']}/{s['disk_total']})\n"
                   f"⚙️ *Load:* {s['load']}\n"
                   f"━━━━━━━━━━━━━━\n"
                   f"⏱️ *Uptime:* {s['uptime']}\n"
                   f"🏠 *Local IP:* `{s['local_ip']}`\n"
                   f"🌐 *Public IP:* `{s['public_ip']}`") # <--- NEW LINE
            
            bot.reply_to(message, msg, parse_mode='Markdown')
