import sqlite3
import khayyam

# ========== GLOBAL DATABASE CONNECTION ==========
conn = sqlite3.connect("database.db", check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")

# ========== DATABASE SETUP ==========


def setup_database():

    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "user_number INTEGER PRIMARY KEY AUTOINCREMENT,"
        "name TEXT,"
        "username TEXT,"
        "chat_id INTEGER UNIQUE,"
        "status INTEGER DEFAULT 1,"
        "drinks_today INTEGER DEFAULT 0,"
        "drinks_total INTEGER DEFAULT 0)"
    )

    conn.commit()


def migrate_database():
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    if "drinks_total" not in columns:
        cursor.execute("ALTER TABLE users RENAME COLUMN drinks TO drinks_total")

    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    chat_type TEXT,
                    title TEXT, 
                    status INTEGER DEFAULT 0
                    )
                   """)

    cursor.execute("""INSERT OR IGNORE INTO chats (
                    chat_id,
                    chat_type,
                    title,
                    status
                    )
                    SELECT
                    chat_id,
                    'private',
                    name,
                    CASE
                        WHEN status='On' THEN 1
                        ELSE 0
                    END
                    FROM users
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


    cursor.execute("UPDATE chats SET status = 1 WHERE status = 'On'")
    cursor.execute("UPDATE chats SET status = 0 WHERE status = 'Off'")
    cursor.execute("UPDATE users SET status = 1 WHERE status = 'On'")
    cursor.execute("UPDATE users SET status = 0 WHERE status = 'Off'")

    conn.commit()


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
    cursor.execute("SELECT * FROM users ORDER BY drinks_total DESC")
    result = cursor.fetchall()

    users = [user for user in result]
    return users



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

    cursor.execute("SELECT drinks_total FROM chats WHERE chat_id=?", (chat_id,))
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

def drinks_today_reset():

    cursor = conn.cursor()

    cursor.execute("UPDATE chats SET drinks_today=0")
    cursor.execute("UPDATE users SET drinks_today=0")

    conn.commit()


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
    date_string = now.strftime("%A %D %B %N")
    return date_string
