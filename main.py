from database import (
    setup_database,
    migrate_database,
    save_user_data,
    user_exists,
    set_user_status,
    get_user_status,
    get_all_users,
    get_all_enabled_users,
    drinks_increment,
    get_today_date,
    get_drinks_today_count,
    get_drinks_total_count,
    drinks_today_reset,
)
from texts import (
    help_command_text,
    start_command_text,
    reminder_texts,
    reminder_keyboard,
    good_morning_text,
    good_night_text,
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
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
    if user_exists(update.message.chat_id) == False:
        save_user_data(
            update.message.chat_id,
            update.message.from_user.first_name,
            update.message.from_user.username,
            "Off",
            0,
            0,
        )
        await update.message.reply_text(
            f"سلام {update.message.from_user.first_name}!{start_command_text}"
        )
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"user <a href='tg://user?id={update.message.from_user.id}'>{update.message.from_user.first_name}</a>, with username {update.message.from_user.username} and ID {update.message.from_user.id} started the bot! ",
            parse_mode="HTML",
        )

    else:
        await update.message.reply_text("قبلا بات رو استارت کردی!")
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"user {update.message.from_user.first_name}, with username {update.message.from_user.username} and ID {update.message.from_user.id} started the bot again. ",
        )


# ========== /HELP COMMAND ==========


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_command_text)


# ========== /TODAY COMMAND ==========


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"""امروز {get_today_date()} است.

 تعداد آب‌های امروز: {get_drinks_today_count(chat_id)}
 تعداد کل آب‌ها: {get_drinks_total_count(chat_id)}""")


# ========== DAILY GM GN MESSAGES ==========


async def daily_message(context: ContextTypes.DEFAULT_TYPE):
    if context.job.name == f"morning_{context.job.chat_id}":
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=good_morning_text.format(date=get_today_date()),
        )
    elif context.job.name == f"night_{context.job.chat_id}":
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=good_night_text.format(
                drinks_today=get_drinks_today_count(context.job.chat_id)
            ),
        )


# ========== DRINKING REMINDER MESSAGE SEND ==========


async def drink_water(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(tz)

    if not (9 <= now.hour <= 22):
        return

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=random.choice(reminder_texts),
        reply_markup=reminder_keyboard,
    )


# ========== DRANK BUTTON ==========


async def drank_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    drinks_increment(user.id)
    await query.answer(text="آفرین!")
    await context.bot.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=f"user {user.first_name} just drank water!",
        parse_mode="HTML",
    )
    await query.edit_message_reply_markup(reply_markup=None)


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
    )

    job_queue.run_daily(
        daily_message,
        time=time(8, 0, tzinfo=tz),
        chat_id=chat_id,
        name=f"morning_{chat_id}",
    )

    job_queue.run_daily(
        daily_message,
        time=time(23, 0, tzinfo=tz),
        chat_id=chat_id,
        name=f"night_{chat_id}",
    ),


async def enable_reminding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job_name = f"remind_{update.effective_chat.id}"
    chat_id = update.message.chat_id
    jobs = context.job_queue.get_jobs_by_name(job_name)
    status = get_user_status(chat_id)

    if status == "On" and jobs:
        await update.message.reply_text(
            "قبلا روشن کردیا.", reply_to_message_id=update.message.message_id
        )
        return

    else:

        set_user_status(update.message.chat_id, "On")
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

        set_user_status(update.message.chat_id, "Off")
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


# ========== ADMIN STUFF ==========
#         to get all users


async def show_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    if chat_id in ADMINS:
        users_list = []
        for user in get_all_users():
            users_list.append(
                f"""{user[0]}. <a href="tg://user?id={user[3]}">{user[1]}</a>, @{user[2]}, (<code>{user[3]}</code>)
status: {user[4]}
drinks today: {user[5]}
drinks in total: {user[6]}
"""
            )
        users_list_text = "\n".join(users_list)

        await context.bot.send_message(
            chat_id=chat_id, text=users_list_text, parse_mode="HTML"
        )

    else:
        pass


#         to send a message from admin to all users


async def send_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    user_ids = []
    for user in get_all_users():
        user_ids.append(int(user[3]))
    if chat_id in ADMINS:
        for user_id in user_ids:
            try:
                text = update.message.text.replace("/admin_message ", "")
                await context.bot.send_message(chat_id=user_id, text=text)

            except Exception as e:
                await context.bot.send_message(
                    chat_id=chat_id, text=f"failed to send message to {user_id}: {e}"
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
app.add_handler(CallbackQueryHandler(drank_button))

app.run_polling()
