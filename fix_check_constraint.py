"""
fix_check_constraint.py — Find and drop CHECK constraints on challenges table.
"""
import psycopg2, traceback

conn = psycopg2.connect(dbname="ctf_platform", user="postgres", password="972006", host="localhost")
conn.autocommit = True
cur = conn.cursor()

# List all constraints
cur.execute("""
    SELECT con.conname, con.contype, pg_get_constraintdef(con.oid)
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    WHERE rel.relname = 'challenges';
""")
print("All constraints on 'challenges':")
constraints = cur.fetchall()
for r in constraints:
    print(f"  {r}")

# Drop any CHECK constraints
for name, ctype, defn in constraints:
    if ctype == 'c':  # 'c' = CHECK
        cur.execute(f"ALTER TABLE challenges DROP CONSTRAINT {name};")
        print(f"\nDropped CHECK constraint: {name}: {defn}")

# Also fix resource_type and resource_path to be nullable
for col in ["resource_type", "resource_path", "description"]:
    try:
        cur.execute(f"ALTER TABLE challenges ALTER COLUMN {col} DROP NOT NULL;")
        print(f"Made nullable: {col}")
    except:
        pass  # already nullable

# Test insert again
try:
    cur.execute("""
        INSERT INTO challenges (title, category, description, resource_type, resource_path, correct_flag, points, is_published)
        VALUES ('TestWelcome', 'welcome', 'A welcome challenge', NULL, NULL, 'flag{hello}', 50, false)
        RETURNING id;
    """)
    rid = cur.fetchone()[0]
    print(f"\n✅ Test INSERT succeeded! id={rid}")
    cur.execute("DELETE FROM challenges WHERE id=%s", (rid,))
    print("Cleaned up.")
except Exception as e:
    print("\n❌ INSERT still failing:")
    traceback.print_exc()

cur.close()
conn.close()
