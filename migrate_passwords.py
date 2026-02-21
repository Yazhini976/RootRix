"""
migrate_passwords.py
────────────────────
One-time script to hash all plain-text passwords in the DB using bcrypt.

Run ONCE before starting the CTF:
    python migrate_passwords.py

After this runs, auth.py will automatically use bcrypt verification.
"""

import bcrypt
import psycopg2

DB_CONFIG = {
    "dbname":   "ctf_platform",
    "user":     "postgres",
    "password": "972006",
    "host":     "localhost",
}

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()

    cur.execute("SELECT id, username, password FROM users")
    users = cur.fetchall()

    updated = 0
    skipped = 0

    for user_id, username, password in users:
        if password.startswith("$2b$") or password.startswith("$2a$"):
            print(f"  [SKIP]    {username} — already hashed")
            skipped += 1
            continue

        hashed = hash_password(password)
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
        print(f"  [HASHED]  {username}")
        updated += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n✅ Done! {updated} passwords hashed, {skipped} already hashed.")

if __name__ == "__main__":
    main()
