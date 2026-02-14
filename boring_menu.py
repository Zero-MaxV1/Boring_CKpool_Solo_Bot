import telebot
from telebot.types import BotCommand

# --- MASTER COMMAND LIST ---
# Edit this list to update BOTH the Menu Button and the /help message at once.
COMMAND_LIST = [
    ('stats',  '⛏️ Live Miner Dashboard'),
    ('miner1', '🔥 Heater 1 Detail'),
    ('miner2', '🔥 Heater 2 Detail'),
    ('planes', '✈️ Scan Local Airspace'),
    ('burn',   '💸 Electricity Cost Calc'),
    ('health', '❤️ System Vital Signs'),
    ('menu',   '🔄 Reload Menu / Help')
]

def update_commands(bot):
    """ Push the command list to the Telegram UI (Blue Button) """
    try:
        commands = [BotCommand(cmd, desc) for cmd, desc in COMMAND_LIST]
        bot.set_my_commands(commands)
        print("✅ Telegram Menu Button Updated.")
    except Exception as e:
        print(f"❌ Failed to update menu: {e}")

def register_handlers(bot):
    """ Handles /help and /menu commands """
    
    @bot.message_handler(commands=['help', 'menu', 'start'])
    def handle_help(message):
        # Dynamically build the text from the Master List
        txt = "🤖 *Boring-Server Command List*\n"
        txt += "━━━━━━━━━━━━━━\n"
        
        for cmd, desc in COMMAND_LIST:
            txt += f"/{cmd} - {desc}\n"
            
        bot.reply_to(message, txt, parse_mode='Markdown')
