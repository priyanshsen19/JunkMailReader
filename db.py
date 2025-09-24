import sqlite3
from contextlib import closing

DB_PATH = "emails.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS emails (
    id TEXT PRIMARY KEY,
    sender TEXT,
    to_field TEXT,
    subject TEXT,
    snippet TEXT,
    internal_date INTEGER,
    is_read INTEGER,
    labels TEXT
)
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    with closing(conn.cursor()) as cur:
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
    return conn

def upsert_email(conn, email):
    with closing(conn.cursor()) as cur:
        cur.execute(
            """
            INSERT OR REPLACE INTO emails
            (id, sender, to_field, subject, snippet, internal_date, is_read, labels)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email["id"],
                email.get("sender"),
                email.get("to_field"),
                email.get("subject"),
                email.get("snippet"),
                email.get("internal_date"),
                1 if email.get("is_read") else 0,
                ",".join(email.get("labels", [])),   # <-- store labels as CSV string
            ),
        )
        conn.commit()

def fetch_all_emails(conn):
    with closing(conn.cursor()) as cur:
        cur.execute(
            "SELECT id, sender, to_field, subject, snippet, internal_date, is_read, labels FROM emails"
        )
        rows = cur.fetchall()
    return [
        {
            "id": r[0],
            "sender": r[1],
            "to_field": r[2],
            "subject": r[3],
            "snippet": r[4],
            "internal_date": r[5],
            "is_read": bool(r[6]),
            "labels": r[7].split(",") if r[7] else [],
        }
        for r in rows
    ]
