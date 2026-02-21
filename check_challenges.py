import psycopg2
conn = psycopg2.connect(dbname="ctf_platform", user="postgres", password="972006", host="localhost")
cur = conn.cursor()
cur.execute("SELECT id, title, category, is_published FROM challenges ORDER BY id;")
rows = cur.fetchall()
print("id | title | category | is_published")
print("-" * 50)
for r in rows:
    print(r)
cur.close(); conn.close()
