import math
import requests
import boring_config  # Imports your settings

def get_live_data():
    price = 0; net_diff = 0
    headers = {'User-Agent': boring_config.USER_AGENT}
    try:
        r = requests.get("https://mempool.space/api/v1/prices", headers=headers, timeout=5)
        price = float(r.json()['USD'])
    except: pass
    try:
        r = requests.get("https://mempool.space/api/v1/mining/difficulty-adjustment", headers=headers, timeout=5)
        net_diff = float(r.json()['difficulty'])
    except: 
        if net_diff == 0: net_diff = boring_config.DEFAULT_DIFFICULTY
    return price, net_diff

def calculate_burn(my_hashrate_th):
    try:
        btc_price, net_diff = get_live_data()
        
        # 1. Electric Costs (Using Config)
        kw = boring_config.TOTAL_WATTS / 1000.0
        daily_cost = kw * 24 * boring_config.KWH_PRICE
        monthly_cost = daily_cost * 30.4
        
        # 2. Probability
        difficulty_hashes = net_diff * (2**32)
        my_hashes_per_sec = my_hashrate_th * 1e12
        
        if my_hashes_per_sec > 0:
            seconds_to_block = difficulty_hashes / my_hashes_per_sec
            years_to_block = (seconds_to_block / 86400) / 365.25
            prob_24h = 1 - math.exp(-86400 / seconds_to_block)
        else:
            years_to_block = 999; prob_24h = 0

        return (f"💸 *The Gambler's Reality*\n"
                f"━━━━━━━━━━━━━━\n"
                f"⚡ *Power Burn:* ${daily_cost:.2f}/day\n"
                f"🗓️ *Monthly Bill:* ${monthly_cost:.2f}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🎰 *Jackpot Odds ({net_diff/1e12:.0f}T)*\n"
                f"• Est. Time to Win: *{years_to_block:.1f} Years*\n"
                f"• 24h Win Chance: *{prob_24h*100:.4f}%*\n"
                f"• BTC Price: ${btc_price:,.0f}")
    except Exception as e:
        return f"❌ Error: {e}"

# --- PLUGIN REGISTRATION ---
def register_handlers(bot):
    @bot.message_handler(commands=['burn'])
    def handle_burn(message):
        if str(message.chat.id) == boring_config.CHAT_ID:
            # Uses Default Hashrate from Config
            report = calculate_burn(boring_config.DEFAULT_HASHRATE) 
            bot.reply_to(message, report, parse_mode='Markdown')
