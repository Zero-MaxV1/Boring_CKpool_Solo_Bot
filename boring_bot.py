import telebot
import time
import boring_config

# Import Plugins
import boring_menu
import boring_economics
import boring_adsb
import boring_stats
import boring_system

# Initialize
bot = telebot.TeleBot(boring_config.TOKEN)

# --- REGISTER HANDLERS ---
# Now 'boring_menu' handles /help and /start automatically
boring_menu.register_handlers(bot) 
boring_economics.register_handlers(bot)
boring_adsb.register_handlers(bot)
boring_stats.register_handlers(bot)
boring_system.register_handlers(bot)

# --- START BACKGROUND THREADS ---
boring_stats.start_threads(bot)
boring_adsb.start_adsb_monitor(bot)

# --- UPDATE UI ---
# Pushes the button layout to Telegram servers on startup
boring_menu.update_commands(bot)

# --- NOTIFICATION ---
try:
    bot.send_message(boring_config.CHAT_ID, "♻️ *Boring-Server Online*\nSystem Rebooted Successfully.", parse_mode='Markdown')
except: pass

# --- MAIN LOOP ---
print("BoringStatsBot Pro Active...")
while True:
    try:
        bot.polling(non_stop=True, interval=2, timeout=20)
    except Exception as e:
        print(f"Bot Polling Error: {e}")
        time.sleep(5)
