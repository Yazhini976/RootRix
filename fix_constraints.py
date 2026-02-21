"""
fix_constraints.py — Fix NOT NULL constraints on optional columns in challenges.
"""
import psycopg2, traceback

conn = psycopg2.connect(dbname="ctf_platform", user="postgres", password="972006", host="localhost")
conn.autocommit = True
cur = conn.cursor()

# Show all columns and their nullable status
cur.execute("""
    SELECT column_name, is_nullable, column_default
    FROM information_schema.columns WHERE table_name='challenges'
    ORDER BY ordinal_position
""")
print("Current schema:")
for r in cur.fetchall():
    print(f"  {r[0]}: nullable={r[1]}  default={r[2]}")

# Make optional columns nullable
nullable_cols = ["description", "resource_type", "resource_path"]
for col in nullable_cols:
    try:
        cur.execute(f"ALTER TABLE challenges ALTER COLUMN {col} DROP NOT NULL;")
        print(f"  Fixed: {col} -> now nullable")
    except Exception as e:
        print(f"  {col}: {e}")

# Make sure is_published has a proper default
try:
    cur.execute("ALTER TABLE challenges ALTER COLUMN is_published SET DEFAULT FALSE;")
    print("  Fixed: is_published default = false")
except Exception as e:
    print(f"  is_published default: {e}")

# Test a raw insert now
try:
    cur.execute("""
        INSERT INTO challenges (title, category, description, resource_type, resource_path, correct_flag, points, is_published)
        VALUES ('TestWelcome', 'welcome', 'A welcome challenge', NULL, NULL, 'flag{hello}', 50, false)
        RETURNING id;
    """)
    rid = cur.fetchone()[0]
    print(f"\nTest INSERT succeeded! id={rid}")
    cur.execute("DELETE FROM challenges WHERE id=%s", (rid,))
    print("Cleaned up.")
except Exception as e:
    print("\nTest INSERT STILL FAILING:")
    traceback.print_exc()

cur.close()
conn.close()
print("\nDone.")
