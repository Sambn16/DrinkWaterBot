from telegram import *
from telegram.ext import *
from dotenv import load_dotenv
import os
import datetime
import time
import random
import khayyam
import pytz
import sqlite3


load_dotenv()
token = os.getenv("BOT_TOKEN")
application = ApplicationBuilder().token(token).build()

jq = application.job_queue

now = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
dform = now.strftime('%Y-%m-%d')
tform = now.strftime('%H:%M:%S')
print(f"bot started at {dform} {tform} ...")

def setup_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users ("
                   "user_number INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "name TEXT,"
                   "username TEXT,"
                   "chatId INTEGER,"
                   "status TEXT DEFAULT 'Off',"
                   "drank INTEGER DEFAULT 0)"
    )
    conn.commit()
    conn.close()


setup_database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    FirstName = update.message.chat.first_name
    LastName = update.message.chat.last_name
    username = update.message.chat.username
    name = f"{FirstName} {LastName}"
    chatId = update.effective_chat.id
    now = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
    tform = now.strftime('%H:%M:%S')
    text = f"user {FirstName}, with id number: {chatId} and username @{username},  started the bot at {tform}"
    print(text)
    await context.bot.send_message(chat_id= -1001925381494, text= text)
    if not user_exists(chatId):

        save_user(chatId, name, username, status="Off", drank=0)

        await context.bot.send_message(chat_id= chatId,text=f"""سلام {FirstName}!

همونطور که می‌دونی من یه رباتم که باید یادت بندازه آب بخوری و سالم بمونی.
برای یادگیری دستوراتم /help رو بزن.
""")
    else:
        await context.bot.send_message(chat_id=chatId, text=f"{FirstName} عزیز قبلا بات رو استارت کردی.")

async def day(update, context):

    FirstName = update.message.chat.first_name
    now = khayyam.JalaliDatetime.today()
    date_string = now.strftime('%A %D %B %N')
    await context.bot.send_message(chat_id=update.effective_chat.id, text = f"امروز {date_string} است.")

async def help(update, context):
    message = """
    خب خب. خیلی خوشحالم که قراره واقعا این کار رو بکنم ^^ درواقع کاری که قراره بکنم اینه که اول صبح بهت تاریخ امروز رو بگم و بهت بگم که قراره حسابی امروز آب بخوری. چجوری؟ اینجوری که من هر ساعت از صبح تا آخر xشب بهت یادآوری میکنم که آب بخوری وگرنه...^^ به هر حال، این پایین لیست دستورات منه
    
    /start برای اینکه بات رو روشن کنی واضحا 
    /on برای اینکه یادآور رو روشن کنی 
    /today برای اینکه تاریخ امروز رو بهت بگم 
    /off ...برای اینکه بات رو خاموش کنی که بهتره نکنی وگرنه """

    chatId = update.effective_chat.id
    await context.bot.send_message(chat_id= chatId, text= message)

async def remind(context: ContextTypes.DEFAULT_TYPE):

    now = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
    tform = now.strftime('%H:%M:%S')
    chatId = context.job.chat_id
    message = random.choice(["آب بخور", "آب بخور عزیزم", "پاشو آب بخور", "آب.", "آب بخور 😡", "آب بخور ناناز", "وقت آبه!", "آب!", "آب؟", "آب بخور 🔪", "باید آب بخورید جناب."])
    keyboard = [
        [InlineKeyboardButton("خوردم!", callback_data="drank")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id= chatId, text = message, reply_markup= reply_markup)
    print(f"message sent to user at {tform} .")

async def button(update, context):
    query = update.callback_query
    FirstName = query.from_user.first_name

    userId = query.from_user.id
    increment_drank(userId)

    msg = "آفرین!"
    await context.bot.send_message(chat_id= -1001925381494, text=f"user {FirstName} drank water")
    await query.answer(text= msg)
    



async def gm(context: ContextTypes.DEFAULT_TYPE):

    now = khayyam.JalaliDatetime.today()
    date_string = now.strftime('%A %D %B')
    chatId = context.job.chat_id
    message = f"""صبح بخیر!
امروز {date_string}ه
برای یه روز پرآب آماده‌ای؟"""
    await context.bot.send_message(chat_id= chatId, text= message)
    

async def on(update, context):
    status = True
    chatId = update.effective_chat.id
    set_chat_status(chatId, 'On')
    text = """خیلی خب!
 از این به بعد از ساعت ۸ صبح تا ۱۰ شب یادت میندازم که آب بخوری. نمی‌ذارم دیگه یادت بره."""
    await context.bot.send_message(chat_id= chatId, text= text)
    print("user sent the on command")
    user_status = get_chat_status(chatId)

    if user_status == "On" and status:
        
        jq.run_daily(gm, time = datetime.time(hour= 8, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 9, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 10, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 11, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 12, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 13, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 14, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 15, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 16, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 17, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 18, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 19, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 20, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 21, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(remind, time = datetime.time(hour= 22, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)
        jq.run_daily(lateNight, time = datetime.time(hour= 23, minute= 00, tzinfo=pytz.timezone('Asia/Tehran')), days=(0, 1, 2, 3, 4, 5, 6), chat_id= chatId)

    else:
        pass



async def off(update, context):
    FirstName = update.message.chat.first_name
    username = update.message.chat.username
    chatId = update.effective_chat.id
    set_chat_status(chatId, 'Off')
    now = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
    tform = now.strftime('%H:%M:%S')
    text = f"user {FirstName}, with id number: {chatId} and username @{username},  turned off the bot at {tform}"
    
    await context.bot.send_message(chat_id= -1001925381494, text= text)
    await context.bot.send_message(chat_id=chatId, text = "اه! خیلی حیف شد. باشه دیگه از این به بعد یادت نمی‌اندازم.")


def increment_drank(chatId):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET drank=drank+1 WHERE chatId=?", (chatId,))

    conn.commit()
    conn.close()

def get_drank_count(chatId):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT drank FROM users WHERE chatId=?", (chatId,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0

def reset_drank(chatId):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET drank=0 WHERE chatId=?", (chatId,))

    conn.commit()
    conn.close()

def set_chat_status(chatId, status):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET status=? WHERE chatId=?", (status, chatId))

    conn.commit()
    conn.close()

def user_exists(chatId):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE chatId=?", (chatId,))
    result = cursor.fetchone()

    conn.close()

    return result is not None

def save_user(chatId, name, username, status, drank):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (name, username, chatId, status, drank) "
                   "VALUES (?, ?, ?, ?, ?)",
                   (name, username, chatId, status, drank))

    conn.commit()
    conn.close()

def get_all_chat_ids():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT chatId FROM users")
    result = cursor.fetchall()

    conn.close()

    chatIds = [row[0] for row in result]

    return chatIds

all_chat_ids = get_all_chat_ids()

async def adminmsg(update, context):

    message_text = update.message.text
    text = message_text.replace("/admin ", "")
    senderId = update.effective_chat.id
    for chatId in all_chat_ids:
        await context.bot.send_message(chat_id= chatId, text=text) 

async def lateNight(update, context):
    now = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
    tform = now.strftime('%H:%M:%S')
    chatId = context.job.chat_id
    drank_count = get_drank_count(chatId)
    text = f"امروز {drank_count} بار آب خوردی. الان هم که دیگه وقت خوابه. شب بخیر! "
    await context.bot.send_message(chat_id= chatId, text=text)
    reset_drank(chatId)


def get_chat_status(chatId):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM users WHERE chatId=?", (chatId,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 'Off'





application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('on', on))
application.add_handler(CommandHandler('today', day))
application.add_handler(CommandHandler('help', help))
application.add_handler(CommandHandler('off', off))
application.add_handler(CommandHandler('admin', adminmsg))
application.add_handler(CallbackQueryHandler(button))



application.run_polling()

