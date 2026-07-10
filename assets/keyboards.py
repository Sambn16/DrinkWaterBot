from telegram import InlineKeyboardButton, InlineKeyboardMarkup


settings_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖ ساعت شروع", callback_data="settings:minus:start_hour"),
            InlineKeyboardButton("ساعت شروع ➕", callback_data="settings:plus:start_hour")
        ],
        [
            InlineKeyboardButton("➖ ساعت پایان", callback_data="settings:minus:end_hour"),
            InlineKeyboardButton("ساعت پایان ➕", callback_data="settings:plus:end_hour")
        ],
        [
            InlineKeyboardButton("➖ تعداد ریمایندر", callback_data="settings:minus:total_reminders"),
            InlineKeyboardButton("تعداد ریمایندر ➕", callback_data="settings:plus:total_reminders")
        ]
    ])