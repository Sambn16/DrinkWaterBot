# 💧 DrinkWaterBot

A Telegram bot that helps users build a healthy water-drinking habit through hourly reminders, personal statistics, and group leaderboards.

## Features

### 👤 Personal reminders

* Hourly reminders to drink water (configurable schedule)
* Good morning and good night messages
* Enable/disable reminders with commands
* Prevents claiming the same reminder more than once
* Daily and lifetime water intake tracking

### 👥 Group support

* Works in groups and supergroups
* Members can tap **"I Drank Water"** independently
* Tracks which members have participated
* Calculates:

  * Total group drinks today
  * Total lifetime group drinks
* Daily and all-time leaderboards

### 📊 Statistics

* Personal:

  * Drinks today
  * Total drinks
* Group:

  * Today's total
  * Overall total
  * Daily leaderboard
  * All-time leaderboard

### 🛠 Admin features

* Broadcast message to all users
* View all registered users
* Startup logging
* Activity logging

---

## Tech Stack

* Python 3.13
* python-telegram-bot (PTB)
* SQLite3
* Khayyam (Jalali dates)
* python-dotenv
* pytz

---

## Database Design

### users

Stores private users.

| Column       | Description               |
| ------------ | ------------------------- |
| user_number  | Auto increment ID         |
| chat_id      | Telegram User ID          |
| name         | First name                |
| username     | Username                  |
| status       | Reminder enabled/disabled |
| drinks_today | Daily drinks              |
| drinks_total | Lifetime drinks           |

### chats

Stores every chat the bot knows.

This includes:

* Private chats
* Groups
* Supergroups

| Column    | Description                  |
| --------- | ---------------------------- |
| chat_id   | Telegram Chat ID             |
| chat_type | private / group / supergroup |
| title     | Chat title                   |
| status    | Reminder enabled             |

### chat_members

A many-to-many relationship between users and groups.

Only members who have actually interacted with the bot (drank water) are stored.

| chat_id | user_id |

---

### reminder_claims

Stores who claimed each reminder.

This prevents users from pressing the reminder button multiple times.

---

## Commands

| Command        | Description             |
| -------------- | ----------------------- |
| `/start`       | Register the user       |
| `/help`        | Show help               |
| `/enable`      | Enable reminders        |
| `/disable`     | Disable reminders       |
| `/today`       | Show today's statistics |
| `/leaderboard` | Show group leaderboard  |

---

## How Group Tracking Works

Unlike most bots, the bot **does not keep a list of every member in a group**.

Instead:

1. A reminder is posted.
2. Members tap **"I Drank Water"**.
3. The user is linked to that group in the `chat_members` table.
4. Group statistics are calculated dynamically by summing the drinks of linked users.

This keeps the database lightweight while still allowing accurate leaderboards and statistics.

---

## Future Ideas

* Weekly/monthly leaderboards
* Achievement badges
* Streak system
* Water intake goals
* Charts and analytics
* Multi-language support
* PostgreSQL migration
* Docker deployment

---

## Project Status

🚧 Currently under active development.

The project is evolving from a personal reminder bot into a feature-rich Telegram habit tracker with group competitions and statistics.
