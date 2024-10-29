import telebot
from datetime import datetime

API_TOKEN = '7854423313:AAEsLifCpL6k__bzG1KEWlwigfQq5mqg15M'
bot = telebot.TeleBot(API_TOKEN)
CHANNEL_ID = "@PPSAVDOROBO"

orders = {}
user_points = {}
admin_ids = [5558925152]  
referal_links = {}
def check_subscription(chat_id):
    try:
        user_status = bot.get_chat_member(CHANNEL_ID, chat_id).status
        if user_status in ['member', 'administrator', 'creator']:
            return True  
        else:
            return False  
    except:
        return False  
def prompt_subscription(chat_id):
    bot.send_message(chat_id, f"Iltimos, avval {CHANNEL_ID} kanaliga obuna bo'ling, so'ngra botdan foydalanishingiz mumkin.")
def generate_report():
    total_orders = len(orders)
    completed_orders = sum(1 for order in orders.values() if order.get('holat') == 'Bajarildi')
    canceled_orders = sum(1 for order in orders.values() if order.get('holat') == 'Bekor qilindi')
    
    report = f"Buyurtmalar hisoboti:\n" \
             f"Jami buyurtmalar: {total_orders}\n" \
             f"Bajarilgan buyurtmalar: {completed_orders}\n" \
             f"Bekor qilingan buyurtmalar: {canceled_orders}"
    
    return report

def update_user_points(chat_id, uc_amount):
    points_per_uc = 50 / 325  
    if chat_id in user_points:
        user_points[chat_id] += int(uc_amount * points_per_uc)
    else:
        user_points[chat_id] = int(uc_amount * points_per_uc)
def generate_referal_link(chat_id):
    return f"http://t.me/YOUR_BOT_NAME?start={chat_id}"

@bot.message_handler(commands=['taklifnoma'])
def give_referal_link(message):
    chat_id = message.chat.id
    if check_subscription(chat_id):
        referal_link = generate_referal_link(chat_id)
        referal_links[chat_id] = referal_link
        bot.reply_to(message, f"Sizning taklifnomangiz:\n{referal_link}")
    else:
        prompt_subscription(chat_id)

@bot.message_handler(commands=['start'])
def start_bot(message):
    chat_id = message.chat.id
    if check_subscription(chat_id):
        if len(message.text.split()) > 1:
            referrer_id = int(message.text.split()[1])
            if referrer_id in user_points:
                user_points[referrer_id] += 50  
                bot.send_message(referrer_id, "Sizning taklifnomangiz orqali yangi foydalanuvchi qo'shildi! 50 ball qo'shildi.")
        bot.reply_to(message, "Xush kelibsiz! Buyurtma berish uchun  uc deb yozing bosing.")
    else:
        prompt_subscription(chat_id)

@bot.message_handler(func=lambda message: True)
def take_order(message):
    chat_id = message.chat.id
    if check_subscription(chat_id):
        if chat_id not in orders:
            orders[chat_id] = {"foydalanuvchi": message.from_user.username}
            bot.reply_to(message, "Iltimos, o'yinchi ID-ni kiriting.")
        
        elif "oyinchi_id" not in orders[chat_id]:
            orders[chat_id]["oyinchi_id"] = message.text
            bot.reply_to(message, "Kerakli UC miqdorini kiriting.")
        
        elif "uc_miqdori" not in orders[chat_id]:
            try:
                uc_miqdori = int(message.text)
                orders[chat_id]["uc_miqdori"] = uc_miqdori
                update_user_points(chat_id, uc_miqdori)  
                bot.reply_to(message, "Buyurtmangizni tasdiqlang. Ha/Yo'q?")
            except ValueError:
                bot.reply_to(message, "Iltimos, to'g'ri UC miqdorini kiriting.")
        
        elif "tasdiq" not in orders[chat_id]:
            if message.text.lower() == "ha":
                orders[chat_id]["tasdiq"] = True
                orders[chat_id]["holat"] = "Bajarildi"
                bot.reply_to(message, "Buyurtmangiz qabul qilindi. Tez orada admin siz bilan bog'lanadi.")
                for admin_id in admin_ids:
                    bot.send_message(admin_id, f"Yangi buyurtma!\nFoydalanuvchi: @{orders[chat_id]['foydalanuvchi']}\nO'yinchi ID: {orders[chat_id]['oyinchi_id']}\nUC miqdori: {orders[chat_id]['uc_miqdori']}")
            elif message.text.lower() == "yo'q":
                bot.reply_to(message, "Buyurtma bekor qilindi.")
                del orders[chat_id]
            else:
                bot.reply_to(message, "Iltimos, 'ha' yoki 'yo'q' deb javob bering.")
    else:
        prompt_subscription(chat_id)

@bot.message_handler(commands=['reyting'])
def show_user_ranking(message):
    chat_id = message.chat.id
    if check_subscription(chat_id):
        if chat_id in user_points:
            points = user_points[chat_id]
            bot.reply_to(message, f"Sizning umumiy ballaringiz: {points}")
        else:
            bot.reply_to(message, "Siz hali ballarga ega emassiz.")
    else:
        prompt_subscription(chat_id)

@bot.message_handler(commands=['hisobot'])
def send_report(message):
    chat_id = message.chat.id
    if check_subscription(chat_id):
        if chat_id in admin_ids:
            report = generate_report()
            bot.reply_to(message, report)
        else:
            bot.reply_to(message, "Siz admin emassiz!")
    else:
        prompt_subscription(chat_id)


bot.polling(none_stop=True, skip_pending=True)
