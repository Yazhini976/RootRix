import psycopg2, traceback

conn = psycopg2.connect(dbname="ctf_platform", user="postgres", password="972006", host="localhost")
conn.autocommit = True
cur = conn.cursor()

# Try inserting with ALL possible columns to see what fails
tests = [
    # Most complete insert
    ("INSERT INTO challenges (title, category, description, resource_type, resource_path, correct_flag, points, is_published) VALUES ('T', 'welcome', 'desc', NULL, NULL, 'flag{t}', 10, false) RETURNING id", "Full INSERT"),
    ("INSERT INTO challenges (title, category, correct_flag, points) VALUES ('T2', 'welcome', 'flag{t2}', 10) RETURNING id", "Minimal INSERT"),
]

for sql, label in tests:
    try:
        cur.execute(sql)
        rid = cur.fetchone()[0]
        print(f"OK: {label} -> id={rid}")
        cur.execute("DELETE FROM challenges WHERE id=%s", (rid,))
    except Exception as e:
        print(f"FAIL: {label}")
        print(f"  ERROR: {e}")

# Show all columns clearly
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns WHERE table_name='challenges'
    ORDER BY ordinal_position
""")
print("\nColumns in challenges table:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} nullable={r[2]} default={r[3]}")

cur.close()
conn.close()
