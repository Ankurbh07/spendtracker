import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expense_tracker.db")


def get_db():
    """Open a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables using CREATE TABLE IF NOT EXISTS."""
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)
    db.commit()
    db.close()


def seed_db():
    """Insert demo user and sample expenses (idempotent)."""
    db = get_db()

    # Skip if demo user already exists
    existing = db.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()

    if existing:
        db.close()
        return

    # Insert demo user
    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo1234")),
    )
    user_id = db.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()["id"]

    # Insert 8 sample expenses
    sample_expenses = [
        (user_id, 12.50,  "Food",          "2026-04-01", "Lunch at café"),
        (user_id, 35.00,  "Transport",     "2026-04-02", "Monthly metro pass top-up"),
        (user_id, 120.00, "Bills",         "2026-04-03", "Electricity bill"),
        (user_id, 800.00, "Bills",         "2026-04-04", "Rent contribution"),
        (user_id, 22.75,  "Health",        "2026-04-05", "Pharmacy — vitamins"),
        (user_id, 15.00,  "Entertainment", "2026-04-07", "Movie ticket"),
        (user_id, 65.00,  "Shopping",      "2026-04-09", "New headphones"),
        (user_id, 8.00,   "Other",         "2026-04-10", "Stationery"),
    ]

    db.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses,
    )
    db.commit()
    db.close()
