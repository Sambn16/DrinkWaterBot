from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import khayyam

# now = khayyam.JalaliDatetime.today()
# date_string = now.strftime('%A %D %B %N')

start_command_text = f"""

همونطور که می‌دونی من یه رباتم که باید یادت بندازه آب بخوری و سالم بمونی.
برای یادگیری دستوراتم /help رو بزن."""


help_command_text = """خب خب. خیلی خوشحالم که واقعا قراره این کار رو بکنم!
 درواقع کاری که قراره بکنم اینه که اول صبح بهت تاریخ امروز رو بگم و بهت بگم که قراره حسابی امروز آب بخوری. چجوری؟ اینجوری که من هر ساعت از صبح تا آخر شب بهت یادآوری میکنم که آب بخوری. به هر حال، این پایین لیست دستورات منه 🔽

/start 
          شروع کار با بات (واضحا)
/help 
         یادگیری دستورات (همین الان زدی!)
/enable          
          روشن کردن ریمایندر
/disable
          خاموش کردن ریمایندر
/today
          تاریخ و آب‌های خورده شده"""


good_morning_text = """صبح بخیر! امروز {date}ه. برای یه روز پرآب آماده‌ای؟ """
good_morning_text_for_groups = """صبحتون بخیر! امروز {date}ه. برای یه روز پرآب آماده‌اید؟ """

reminder_texts = [
    "آب بخور",
    "آب بخور عزیزم",
    "پاشو آب بخور",
    "آب.",
    "آب بخور 😡",
    "آب بخور ناناز",
    "وقت آبه!",
    "آب!",
    "آب؟",
    "آب بخور 🔪",
    "باید آب بخوری.",
    "آآآآآآآآآب",
    "آببببب!",
    "می‌دونی وقت چیه دیگه؟",
]

good_night_text = "امروز {drinks_today} بار آب خوردی. الان هم که دیگه وقت خوابه. شب بخیر!"
good_night_text_for_groups = "امروز {chat_drinks_today} بار آب خوردید. الان هم که دیگه وقت خوابه. شب بخیر!"

group_leaderboard_today_text = """"📅 رده بندی آب‌خورهای امروز!

{leaderboard}
"""
group_leaderboard_text = """🏆 رده بندی کل آب‌خورها!

{leaderboard}
"""


settings_text = """<b>تنظیمات بات</b>

⏰ ساعت شروع: <code>{start_hour}</code>
😴 ساعت پایان: <code>{end_hour}</code>
🔔 تعداد ریمایندر: <code>{total_reminders}</code>
"""



def reminder_keyboard(reminder_id):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("خوردم!", callback_data=f"drank:{reminder_id}")]])
    return keyboard

def leaderboard_keyboard():
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("لیدربورد کل", callback_data="all"), InlineKeyboardButton("لیدربورد امروز", callback_data="today")]])
    return keyboard


