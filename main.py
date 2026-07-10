from database import (
    setup_database,
    migrate_database,
    save_user,
    save_chat,
    update_user_data,
    user_exists,
    set_chat_status,
    get_chat_status,
    get_all_users,
    get_all_enabled_users,
    drinks_increment,
    get_today_date,
    get_drinks_today_count,
    get_drinks_total_count,
    drinks_today_reset,
    has_user_claimed,
    add_claim,
    linking_to_group,
    get_group_drinks_today,
    get_group_drinks_total,
    get_group_leaderboard,
    get_group_leaderboard_all,
    get_all_users_sorted
)
from texts import (
    help_command_text,
    start_command_text,
    reminder_texts,
    reminder_keyboard,
    good_morning_text,
    good_night_text,
    good_night_text_for_groups,
    group_leaderboard_text,
    group_leaderboard_today_text,
    leaderboard_keyboard
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ChatMemberHandler
)
from dotenv import load_dotenv
from datetime import time, timedelta, datetime
import os, random, pytz, sqlite3

# ========== SETUP ==========

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
ADMINS = []
for admin in os.getenv("ADMINS").split(","):
    ADMINS.append(int(admin.strip()))
tz = pytz.timezone("Asia/Tehran")

app = ApplicationBuilder().token(TOKEN).build()

setup_database()
migrate_database()


# ========== /START COMMAND ==========


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        if not user_exists(update.message.chat_id):
            save_user(
                update.message.chat_id,
                update.message.from_user.first_name,
                update.message.from_user.username,
                0,
                0,
                0,
                )

            save_chat(update.message.chat_id, update.message.chat.type, update.message.chat.title, 1)

            await update.message.reply_text(
                f"سلام {update.message.from_user.first_name}!{start_command_text}"
            )
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=f"user <a href='tg://user?id={update.message.from_user.id}'>{update.message.from_user.first_name}</a>, with username @{update.message.from_user.username} and ID {update.message.from_user.id} started the bot! ",
                parse_mode="HTML",
            )

        else:
            save_chat(update.message.chat_id, update.message.chat.type, update.message.chat.title, 1)
            await update.message.reply_text("قبلا بات رو استارت کردی!")
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=f"user {update.message.from_user.first_name}, with username @{update.message.from_user.username} and ID {update.message.from_user.id} started the bot again. ",
            )
    elif update.effective_chat.type == "supergroup" or update.effective_chat.type == "group":
            save_chat(
            update.effective_chat.id,
            update.effective_chat.type,
            update.effective_chat.title or update.effective_chat.first_name,
            0,
            )

# ========== /HELP COMMAND ==========


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_command_text)


# ========== /TODAY COMMAND ==========


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_chat.type == "private":
        await update.message.reply_text(f"""امروز {get_today_date()} است.

    تعداد آب‌های امروز: {get_drinks_today_count(chat_id)}
    تعداد کل آب‌ها: {get_drinks_total_count(chat_id)}""")
        
    else:
        await update.message.reply_text(f"""امروز {get_today_date()} است.

    تعداد آب‌های امروز گروه: {get_group_drinks_today(chat_id)}
    تعداد کل آب‌های گروه: {get_group_drinks_total(chat_id)}""")

# ========== DAILY GM GN MESSAGES ==========


async def daily_message(context: ContextTypes.DEFAULT_TYPE):
    chat = await context.bot.get_chat(context.job.chat_id)

    if context.job.name == f"morning_{context.job.chat_id}":
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=good_morning_text.format(date=get_today_date()),
        )
        
    elif context.job.name == f"night_{context.job.chat_id}":
        if chat.type == "private":
            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=good_night_text.format(
                    drinks_today=get_drinks_today_count(context.job.chat_id)
                ),
            )
            update_user_data(context.job.chat_id, chat.first_name, chat.username)

        elif chat.type in ["group", "supergroup"]:
            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=good_night_text_for_groups.format(
                    chat_drinks_today=get_group_drinks_today(context.job.chat_id)
                ),
            )

    
    


# ========== DRINKING REMINDER MESSAGE SEND ==========


async def drink_water(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(tz)
    last_message_id = context.job.data["last_message_id"]

    if last_message_id is not None:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=context.job.chat_id,
                message_id=last_message_id,
                reply_markup=None,
            )
        except Exception:
            pass

    if not (8 <= now.hour <= 21):
        return

    reminder_id = now.strftime("%Y%m%d%H%M%S")

    message = await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=random.choice(reminder_texts),
        reply_markup=reminder_keyboard(reminder_id),
    )
    context.job.data["last_message_id"] = message.message_id


# ========== DRANK BUTTON ==========


async def drank_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    message = query.message

    
    action, reminder_id = query.data.split(":")

    if not user_exists(user.id):
        await query.answer(text="باید اول بات رو توی پیوی استارت کنی!", show_alert=True)
        return

    if has_user_claimed(user.id, reminder_id):
        await query.answer(text="قبلا آب خوردی!", show_alert=True)
        return

    add_claim(user.id, reminder_id)
    drinks_increment(user.id)

    text = f"آفرین! آب‌های امروزت تا الان: {get_drinks_today_count(user.id)} تا."
    await query.answer(text=text)
    
    if message.chat.type in ["group", "supergroup"]:
        new_text = f"{message.text}\n{user.first_name} آب خورد!"
        linking_to_group(update.effective_chat.id, user.id)
        try:
            await query.edit_message_text(text=new_text, reply_markup=message.reply_markup)
        except:
            pass
    elif message.chat.type == "private":
        await query.edit_message_reply_markup(reply_markup=None)
    username_text = f"@{user.username}" if user.username else "NOT_SET"
    await context.bot.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=f"user {user.first_name} ({username_text}) just drank water!",
        parse_mode="HTML",
    )


# ========== ENABLING THE REMINDER ==========


def seconds_until_next_hour():
    now = datetime.now(tz)
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return int((next_hour - now).total_seconds())


def schedule_user_jobs(job_queue, chat_id):
    job_queue.run_repeating(
        drink_water,
        interval=3600,
        first=seconds_until_next_hour(),
        chat_id=chat_id,
        name=f"remind_{chat_id}",
        data={"last_message_id": None},
    )

    job_queue.run_daily(
        daily_message,
        time=time(8, 0, tzinfo=tz),
        chat_id=chat_id,
        name=f"morning_{chat_id}"
    )

    job_queue.run_daily(
        daily_message,
        time=time(23, 0, tzinfo=tz),
        chat_id=chat_id,
        name=f"night_{chat_id}"
    )


async def enable_reminding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job_name = f"remind_{update.effective_chat.id}"
    chat_id = update.message.chat_id
    jobs = context.job_queue.get_jobs_by_name(job_name)
    status = get_chat_status(chat_id)

    if status == 1 and jobs:
        await update.message.reply_text(
            "قبلا روشن کردیا.", reply_to_message_id=update.message.message_id
        )
        return

    else:

        set_chat_status(update.message.chat_id, 1)
        await update.message.reply_text(
            "ریمایندر روشن شد! از این به بعد از ساعت 9 صبح تا 10 شب یادت میندازم آب بخوری.",
            reply_to_message_id=update.message.message_id,
        )

        schedule_user_jobs(context.job_queue, update.message.chat_id)

        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"user <a href='tg://user?id={update.message.from_user.id}'>{update.message.from_user.first_name}</a>, with username {update.message.from_user.username} and ID {update.message.from_user.id} enabled the reminder.",
            parse_mode="HTML",
        )


# ========== DISABLING THE REMINDER ==========


async def disable_reminding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = []
    job_names = [
        f"remind_{update.effective_chat.id}",
        f"morning_{update.effective_chat.id}",
        f"night_{update.effective_chat.id}",
    ]
    for name in job_names:
        jobs.extend(context.job_queue.get_jobs_by_name(name))

    if jobs:

        for job in jobs:
            job.schedule_removal()

        set_chat_status(update.message.chat_id, 0)
        await update.message.reply_text(
            "ریمایندر خاموش شد :( دیگه یادت نمیندازم آب بخوری. خواستی دوباره روشنش کنی /enable رو بزن.",
            reply_to_message_id=update.message.message_id,
        )
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"user <a href='tg://user?id={update.message.from_user.id}'>{update.message.from_user.first_name}</a>, with username {update.message.from_user.username} and ID {update.message.from_user.id} DISABLED the reminder!!!.",
            parse_mode="HTML",
        )

    else:
        await update.message.reply_text(
            "ریمایندر هنوز نداری. \nکامند /enable رو بزن.",
            reply_to_message_id=update.message.message_id,
        )
        return

# ========== LEADERBOARD ==========

def format_group_leaderboard_text(data):
    text = ""
    for user, (name, drinks_today) in enumerate(data, 1):
        rank = "🥇" if user == 1 else "🥈" if user == 2 else "🥉" if user == 3 else f"{user}."
        text += f"{rank} {name}: {drinks_today} بار.\n"
    return text

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type in ["group", "supergroup"]:
        chat_id = update.effective_chat.id
        data = get_group_leaderboard(chat_id)
        if not data:
            await update.message.reply_text("هیچکس اینجا هنوز آب نخورده! وا؟؟ آب بخورید دیگه.", reply_to_message_id=update.message.message_id)
            return

        

        await update.message.reply_text(group_leaderboard_today_text.format(leaderboard=format_group_leaderboard_text(data)), reply_markup=leaderboard_keyboard())

    else:
        await update.message.reply_text("این کامند فقط برای گروه‌هاست. دلت می‌خواد استفاده کنی؟ من رو به یکی از گروه‌هات اضافه کن!")


# ========== LEADERBOARD BUTTONS ==========

async def leaderboard_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    
    # Check which button was tapped
    if query.data == "today":
        data = get_group_leaderboard(chat_id)
        leaderboard_text = group_leaderboard_today_text
    
    else: # This is the "all" button
        data = get_group_leaderboard_all(chat_id)
        leaderboard_text = group_leaderboard_text
    if not data:
        await query.edit_message_text("هیچ دیتایی موجود نیست.")
    else:
        await query.edit_message_text(
            leaderboard_text.format(leaderboard=format_group_leaderboard_text(data)),
            reply_markup=leaderboard_keyboard()
        )



# ========== ADMIN STUFF ==========
#         to get all users


async def show_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    if chat_id in ADMINS:
        users_list = []
        number = 0
        for user in get_all_users_sorted():
            users_list.append(
                f"""{number}. <a href="tg://user?id={user[3]}">{user[1]}</a>, @{user[2]}, (<code>{user[3]}</code>)
status: {user[4]}
drinks today: {user[5]}
drinks in total: {user[6]}
"""
            )
            number += 1
        users_list_text = "\n".join(users_list)

        await context.bot.send_message(
            chat_id=chat_id, text=users_list_text, parse_mode="HTML"
        )

    else:
        pass


#         to send a message from admin to all users


async def send_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    users = []
    for user in get_all_users():
        users.append(user)
    if chat_id in ADMINS:
        for user in users:
            print(user)
            try:
                text = update.message.text.replace("/admin_message ", "")
                await context.bot.send_message(chat_id=user[3], text=text)

            except Exception as e:
                await context.bot.send_message(
                    chat_id=chat_id, text=f"failed to send message to {user[1]}, @{user[2]} ({user[3]}): {e}"
                )
    else:
        pass


# ========== GROUP SETTINGS ==========

async def track_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = update.my_chat_member.new_chat_member.status

    if status in ["member", "administrator"]:
        chat = update.effective_chat
        save_chat(chat.id, chat.type, chat.title, 1)
        await context.bot.send_message(chat_id=chat.id, text="سلام! خوشحالم که من رو به گروهتون اد کردید. برای یادگیری دستوراتم /help رو بزنید.")
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"group <b>{chat.title}</b>, with id {chat.id} added the bot.",
            parse_mode="HTML",
        )
    else:
        pass



# ========== RESTORING THE JOBS FROM DATABASE ==========
# so it can work after rebooting


def restore_jobs(app):
    users = get_all_enabled_users()
    for chat_id in users:
        schedule_user_jobs(app.job_queue, chat_id)


# ========== RESETTING TODAY'S DRINKS ==========


def reset_daily_stats(context: ContextTypes.DEFAULT_TYPE):
    drinks_today_reset()


app.job_queue.run_daily(reset_daily_stats, time=time(0, 0, tzinfo=tz))


# ========== CONFIGURATIONS & STARTUP ===========

print("bot started...")


async def on_startup(app):
    restore_jobs(app)
    await app.bot.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=f"""bot started successfully at {datetime.now(tz).strftime('%H:%M:%S')}.
        users in database: {len(get_all_users())}""",
    )


app.post_init = on_startup
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("today", today_command))
app.add_handler(CommandHandler("enable", enable_reminding))
app.add_handler(CommandHandler("disable", disable_reminding))
app.add_handler(CommandHandler("all_users", show_all_users))
app.add_handler(CommandHandler("admin_message", send_admin_message))
app.add_handler(CommandHandler("leaderboard", leaderboard_command))
app.add_handler(ChatMemberHandler(track_chat_member))
app.add_handler(
    CallbackQueryHandler(drank_button, pattern=r"^drank:")
)
app.add_handler(
    CallbackQueryHandler(leaderboard_button, pattern=r"^(today|all)$")
)

app.run_polling()
