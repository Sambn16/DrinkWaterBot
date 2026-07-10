import sqlite3
import khayyam
from datetime import datetime

# ========== GLOBAL DATABASE CONNECTION ==========
conn = sqlite3.connect("database.db", check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")

# ========== DATABASE SETUP ==========


def setup_database():
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_number INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT,
            chat_id INTEGER UNIQUE,
            status INTEGER DEFAULT 1,
            drinks_today INTEGER DEFAULT 0,
            drinks_total INTEGER DEFAULT 0,
            start_hour INTEGER DEFAULT 9,
            end_hour INTEGER DEFAULT 22,
            total_reminders INTEGER DEFAULT 14,
            streak_count INTEGER DEFAULT 0,
            cooldown_seconds INTEGER DEFAULT 2160,
            last_drink_time INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            chat_type TEXT,
            title TEXT, 
            status INTEGER DEFAULT 0,
            start_hour INTEGER DEFAULT 9,
            end_hour INTEGER DEFAULT 22,
            total_reminders INTEGER DEFAULT 14
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminder_messages (
            reminder_id TEXT,
            chat_id INTEGER,
            message_id INTEGER,
            chat_type TEXT,
            sent_at TEXT,
            PRIMARY KEY (reminder_id, chat_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminder_claims (
            reminder_id TEXT,
            chat_id INTEGER,
            user_id INTEGER,
            claimed_at TEXT,
            PRIMARY KEY (reminder_id, user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_members (
            chat_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (chat_id, user_id),
            FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
            FOREIGN KEY (user_id) REFERENCES users(chat_id)
        )
    """)

    conn.commit()


def migrate_database():
    # cursor = conn.cursor()
    # cursor.execute("ALTER TABLE chats ADD COLUMN start_hour INTEGER DEFAULT 9;")
    # cursor.execute("ALTER TABLE chats ADD COLUMN end_hour INTEGER DEFAULT 22;")
    # cursor.execute("ALTER TABLE chats ADD COLUMN total_reminders INTEGER DEFAULT 14;    ")
    
    # cursor.execute("ALTER TABLE users ADD COLUMN start_hour INTEGER DEFAULT 9;")
    # cursor.execute("ALTER TABLE users ADD COLUMN end_hour INTEGER DEFAULT 22;")
    # cursor.execute("ALTER TABLE users ADD COLUMN total_reminders INTEGER DEFAULT 14;    ")
    # cursor.execute("ALTER TABLE users ADD COLUMN streak_count INTEGER DEFAULT 0;")
    # cursor.execute("ALTER TABLE users ADD COLUMN cooldown_seconds INTEGER DEFAULT 21600;")
    # cursor.execute("ALTER TABLE users ADD COLUMN last_drink_time TEXT;")
    # conn.commit()
    pass


# ========== USER/CHAT FUNCTIONS ==========


def save_user(chat_id, name, username, status, drinks_today, drinks_total):
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO users (name, username, chat_id, status, drinks_today, drinks_total) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (name, username, chat_id, status, drinks_today, drinks_total),
    )

    conn.commit()


def save_chat(chat_id, chat_type, title, status):
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT OR IGNORE INTO chats
    (chat_id, chat_type, title, status)
    VALUES (?, ?, ?, ?)
    """,
        (chat_id, chat_type, title, status),
    )

    conn.commit()


def linking_to_group(chat_id, user_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO chat_members
        (chat_id, user_id)
        VALUES (?, ?)
        """,
        (chat_id, user_id),
    )
    conn.commit()


def update_user_data(chat_id, name, username):

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET name = ?, username = ?
        WHERE chat_id = ?
    """,
        (name, username, chat_id),
    )
    conn.commit()


def user_exists(chat_id):
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    return result is not None


def set_chat_status(chat_id, status):
    cursor = conn.cursor()

    cursor.execute("UPDATE chats SET status=? WHERE chat_id=?", (status, chat_id))

    conn.commit()


def get_chat_status(chat_id):

    cursor = conn.cursor()

    cursor.execute("SELECT status FROM chats WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    return result[0] if result else 0


def update_user_cooldown(chat_id, cooldown_seconds):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET cooldown_seconds=? WHERE chat_id=?", (cooldown_seconds, chat_id))
    conn.commit()

def update_user_last_drink_time(chat_id, last_drink_time):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_drink_time=? WHERE chat_id=?", (last_drink_time, chat_id))
    conn.commit()


def get_user_cooldown(chat_id):
    cursor = conn.cursor()
    cursor.execute("SELECT cooldown_seconds FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()
    return result if result else (None, 2160)


def check_user_cooldown(chat_id, last_drink_time):
    cursor = conn.cursor()
    cursor.execute("SELECT last_drink_time, cooldown_seconds FROM users WHERE chat_id=?", (chat_id,))
    row = cursor.fetchone()
    if row:
        last_drink_raw, cooldown_seconds = row

        if last_drink_raw and last_drink_raw != "0" and isinstance(last_drink_raw, str):
            last_drink = datetime.fromisoformat(last_drink_raw)
            current = datetime.fromisoformat(last_drink_time)
            time_passed = (current - last_drink).total_seconds()
            if time_passed < cooldown_seconds:
                minutes_left = int((cooldown_seconds - time_passed) / 60)
                return False, (minutes_left if  minutes_left > 0 else 1)
            
        cursor.execute("UPDATE users SET last_drink_time=? WHERE chat_id=?", (last_drink_time, chat_id))
        conn.commit()
        return True, 0
    return False, 0


def reset_chat_stats(chat_id, is_private):
    cursor = conn.cursor()
    if is_private:
        cursor.execute("SELECT drinks_today FROM users WHERE chat_id=?", (chat_id,))
        row = cursor.fetchone()
        drinks_today = row[0] if row else 0

        if drinks_today >= 8:
            cursor.execute("UPDATE users SET streak_count = streak_count + 1 WHERE chat_id = ?", (chat_id,))
        else:
            cursor.execute("UPDATE users SET streak_count = 0 WHERE chat_id = ?", (chat_id,))
                
        
        cursor.execute("UPDATE users SET drinks_today = 0 WHERE chat_id = ?", (chat_id,))
    else:
        cursor.execute("DELETE FROM chat_members WHERE chat_id = ?", (chat_id,))
        
    conn.commit()

# ========== ADMIN STUFF ==========


def get_all_users():

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()

    users = [user for user in result]
    return users


def get_all_enabled_users():

    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM chats WHERE status= 1")
    result = cursor.fetchall()

    chat_ids = [row[0] for row in result]

    return chat_ids

def get_all_users_sorted():

    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, name, username, status, drinks_today, drinks_total FROM users ORDER BY drinks_total DESC")
    return cursor.fetchall()


# ========== USER SETTINGS ==========

def get_chat_settings(chat_id):

    cursor = conn.cursor()
    cursor.execute("SELECT chat_type FROM chats WHERE chat_id = ?", (chat_id,))
    chat_row = cursor.fetchone()
    if chat_row and chat_row[0] in ["group", "supergroup"]:
        cursor.execute("SELECT start_hour, end_hour, total_reminders FROM chats WHERE chat_id = ?", (chat_id,))
    else:
        cursor.execute("SELECT start_hour, end_hour, total_reminders FROM users WHERE chat_id = ?", (chat_id,))

    result = cursor.fetchone()

    return result if result else (9, 22, 14)

def update_chat_settings(chat_id, setting_name, direction):
    """
    تنظیمات مربوط به ساعت شروع، پایان و تعداد ریمایندرها را به‌صورت داینامیک تغییر می‌دهد.
    """
    cursor = conn.cursor()
    

    cursor.execute("SELECT chat_type FROM chats WHERE chat_id = ?", (chat_id,))
    chat_row = cursor.fetchone()
    table = "chats" if (chat_row and chat_row[0] in ["group", "supergroup"]) else "users"
    

    cursor.execute(f"SELECT {setting_name} FROM {table} WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    current_value = row[0] if row else (14 if setting_name == "total_reminders" else (9 if setting_name == "start_hour" else 22))


    change = 1 if direction == "plus" else -1
    new_value = current_value + change


    if setting_name == "total_reminders":
        if new_value < 8 or new_value > 14:
            return False, current_value
        

    elif setting_name in ["start_hour", "end_hour"]:
        if new_value > 23:
            new_value = 0
        elif new_value < 0:
            new_value = 23


    cursor.execute(f"UPDATE {table} SET {setting_name} = ? WHERE chat_id = ?", (new_value, chat_id))
    conn.commit()

    return True, new_value

def get_chat_cooldown_rules(chat_id):
    cursor = conn.cursor()
    cursor.execute("SELECT cooldown_seconds, last_drink_time FROM users WHERE chat_id=?", (chat_id,))
    row = cursor.fetchone()
    return row if row else (2160, 0)


# ========== DRINKS FUNCTIONS ==========


def drinks_increment(chat_id):

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET drinks_total=drinks_total+1 WHERE chat_id=?", (chat_id,)
    )
    cursor.execute(
        "UPDATE users SET drinks_today=drinks_today+1 WHERE chat_id=?", (chat_id,)
    )

    conn.commit()
    cursor.execute("SELECT drinks_today FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()
    
    return result[0] if result else 0


def get_drinks_today_count(chat_id):

    cursor = conn.cursor()

    cursor.execute("SELECT drinks_today FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    return result[0] if result else 0

def get_group_drinks_today(chat_id):
    cursor = conn.cursor()
    # Sum the 'drinks_today' of all users who are members of this chat
    cursor.execute("""
        SELECT SUM(u.drinks_today) 
        FROM users u
        JOIN chat_members cm ON u.chat_id = cm.user_id
        WHERE cm.chat_id = ?
    """, (chat_id,))
    result = cursor.fetchone()
    return result[0] if result and result[0] else 0

def get_drinks_total_count(chat_id):

    cursor = conn.cursor()

    cursor.execute("SELECT drinks_total FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    return result[0] if result else 0

def get_group_drinks_total(chat_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(u.drinks_total) 
        FROM users u
        JOIN chat_members cm ON u.chat_id = cm.user_id
        WHERE cm.chat_id = ?
    """, (chat_id,))
    result = cursor.fetchone()
    return result[0] if result and result[0] else 0



# ========== REMINDER CLAIMS ==========


def add_claim(chat_id, reminder_id):

    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO reminder_claims (reminder_id, user_id) VALUES (?, ?)",
        (reminder_id, chat_id),
    )

    conn.commit()


def has_user_claimed(chat_id, reminder_id):

    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM reminder_claims WHERE reminder_id=? AND user_id=?",
        (reminder_id, chat_id),
    )
    result = cursor.fetchone()

    return result is not None


# ========== LEADERBOARD ==========

def get_group_leaderboard(chat_id):
    cursor = conn.cursor()
    # Join users and chat_members, filter by chat_id, and sort by daily drinks
    cursor.execute("""
        SELECT u.name, u.drinks_today 
        FROM users u
        JOIN chat_members cm ON u.chat_id = cm.user_id
        WHERE cm.chat_id = ? AND u.drinks_today > 0
        ORDER BY u.drinks_today DESC
    """, (chat_id,))
    
    return cursor.fetchall() # Returns a list of (name, drinks_today)


def get_group_leaderboard_all(chat_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.name, u.drinks_total 
        FROM users u
        JOIN chat_members cm ON u.chat_id = cm.user_id
        WHERE cm.chat_id = ? AND u.drinks_total > 0
        ORDER BY u.drinks_total DESC
    """, (chat_id,))
    return cursor.fetchall()



# ========== GETTING TODAY'S DATE ==========


def get_today_date():
    now = khayyam.JalaliDatetime.today()
    date_string = now.strftime("%A %D %B")
    return date_string
