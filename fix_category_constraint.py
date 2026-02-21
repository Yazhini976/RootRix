"""
fix_category_constraint.py — Fix the CHECK constraint on category column to include 'welcome'.
"""
import psycopg2

conn = psycopg2.connect(dbname="ctf_platform", user="postgres", password="972006", host="localhost")
conn.autocommit = True
cur = conn.cursor()

# Find and drop any CHECK constraints on challenges
cur.execute("""
    SELECT con.conname, con.contype, pg_get_constraintdef(con.oid)
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    WHERE rel.relname = 'challenges' AND con.contype = 'c';
""")
check_constraints = cur.fetchall()

print("Found CHECK constraints:")
for name, ctype, defn in check_constraints:
    print(f"  {name}: {defn}")
    cur.execute(f"ALTER TABLE challenges DROP CONSTRAINT \"{name}\";")
    print(f"  -> Dropped: {name}")

# Add new constraint that includes 'welcome'
cur.execute("""
    ALTER TABLE challenges ADD CONSTRAINT challenges_category_check
    CHECK (category IN ('welcome', 'web', 'forensic', 'osint', 'steg', 'crypto'));
""")
print("Added new constraint with 'welcome' included.")

# Test insert
cur.execute("""
    INSERT INTO challenges (title, category, description, resource_type, resource_path, correct_flag, points, is_published)
    VALUES ('TestWelcome', 'welcome', 'test', NULL, NULL, 'flag{test}', 50, false)
    RETURNING id;
""")
rid = cur.fetchone()[0]
print(f"Test INSERT succeeded! id={rid}")
cur.execute("DELETE FROM challenges WHERE id=%s", (rid,))
print("Cleaned up. Done!")

cur.close()
conn.close()
