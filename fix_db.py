"""
fix_db.py — Inspect and repair DB schema to match SQLAlchemy models.
Run once: python fix_db.py
"""
import psycopg2

conn = psycopg2.connect(dbname="ctf_platform", user="postgres", password="972006", host="localhost")
conn.autocommit = True
cur = conn.cursor()

# ── Inspect current columns ──────────────────────────────────────
def get_columns(table):
    cur.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name=%s ORDER BY ordinal_position;",
        (table,)
    )
    return {row[0]: row[1] for row in cur.fetchall()}

print("\n=== challenges columns ===")
chall_cols = get_columns("challenges")
for k, v in chall_cols.items():
    print(f"  {k}: {v}")

print("\n=== submissions columns ===")
sub_cols = get_columns("submissions")
for k, v in sub_cols.items():
    print(f"  {k}: {v}")

# ── Add missing columns ──────────────────────────────────────────
fixes = []

# challenges table
if "is_published" not in chall_cols:
    cur.execute("ALTER TABLE challenges ADD COLUMN is_published BOOLEAN NOT NULL DEFAULT FALSE;")
    fixes.append("challenges.is_published (BOOLEAN DEFAULT FALSE)")

# submissions table
if "earned_points" not in sub_cols:
    cur.execute("ALTER TABLE submissions ADD COLUMN earned_points INTEGER NOT NULL DEFAULT 0;")
    fixes.append("submissions.earned_points (INTEGER DEFAULT 0)")

# settings table
cur.execute("CREATE TABLE IF NOT EXISTS settings (key VARCHAR(100) PRIMARY KEY, value VARCHAR(500) NOT NULL);")
cur.execute("INSERT INTO settings (key, value) VALUES ('leaderboard_visible', 'false') ON CONFLICT (key) DO NOTHING;")
fixes.append("settings table (created if missing)")

if fixes:
    print("\n✅ Fixed:")
    for f in fixes:
        print(f"  + Added {f}")
else:
    print("\n✅ Schema looks correct — no changes needed.")

print("\n=== Final challenges columns ===")
for k, v in get_columns("challenges").items():
    print(f"  {k}: {v}")

cur.close()
conn.close()
print("\nDone.")
