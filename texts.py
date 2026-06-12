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

reminder_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("خوردم!", callback_data="drank")]])