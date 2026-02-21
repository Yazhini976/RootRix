import psycopg2, traceback

conn = psycopg2.connect(dbname="ctf_platform", user="postgres", password="972006", host="localhost")
cur = conn.cursor()

# Show all columns in challenges
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name='challenges'
    ORDER BY ordinal_position;
""")
print("=== challenges columns ===")
for r in cur.fetchall():
    print(r)

# Try raw insert
try:
    cur.execute("""
        INSERT INTO challenges (title, category, correct_flag, points, is_published)
        VALUES ('TestChallenge', 'welcome', 'flag{test}', 10, false)
        RETURNING id;
    """)
    row = cur.fetchone()
    print("\nRaw INSERT succeeded, id =", row[0])
    conn.rollback()
except Exception as e:
    conn.rollback()
    print("\nRaw INSERT failed:")
    traceback.print_exc()

# Show constraints on challenges
cur.execute("""
    SELECT con.conname, con.contype, pg_get_constraintdef(con.oid)
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    WHERE rel.relname = 'challenges';
""")
print("\n=== challenges constraints ===")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
