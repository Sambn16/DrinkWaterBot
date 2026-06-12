import sqlite3
import khayyam


def setup_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users ("
                   "user_number INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "name TEXT,"
                   "username TEXT,"
                   "chat_id INTEGER UNIQUE,"
                   "status TEXT DEFAULT 'Off',"
                   "drinks_today INTEGER DEFAULT 0,"
                   "drinks INTEGER DEFAULT 0)"
    )
    conn.commit()
    conn.close()

def migrate_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    if "drinks_today" not in columns:
        cursor.execute("ALTER TABLE users RENAME COLUMN drank TO drinks_today")
        

    if "drinks" not in columns:
        cursor.execute("ALTER TABLE users ADD drinks TEXT DEFAULT 0")
        
    conn.commit()
    conn.close()


def save_user_data(chat_id, name, username, status, drinks_today, drinks):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (name, username, chat_id, status, drinks_today, drinks) "
                   "VALUES (?, ?, ?, ?, ?, ?)",
                   (name, username, chat_id, status, drinks_today, drinks))

    conn.commit()
    conn.close()


def user_exists(chat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    conn.close()

    return result is not None

def set_user_status(chat_id, status):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET status=? WHERE chat_id=?", (status, chat_id))

    conn.commit()
    conn.close()

def get_user_status(chat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 'Off'

def get_all_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    conn.close()

    users = [user for user in result]
    return users
    

def get_all_enabled_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users WHERE status='On'")
    result = cursor.fetchall()
    conn.close()

    chat_ids = [row[0] for row in result]

    return chat_ids

def drinks_increment(chat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET drinks=drinks+1 WHERE chat_id=?", (chat_id,))
    cursor.execute("UPDATE users SET drinks_today=drinks_today+1 WHERE chat_id=?", (chat_id,))

    conn.commit()
    conn.close()

def get_drinks_today_count(chat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT drinks_today FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0


def get_drinks_total_count(chat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT drinks FROM users WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0


def drinks_today_reset():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET drinks_today=0")

    conn.commit()
    conn.close()


def get_today_date():
    now = khayyam.JalaliDatetime.today()
    date_string = now.strftime('%A %D %B %N')
    return date_string