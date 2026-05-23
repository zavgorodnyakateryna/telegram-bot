import sqlite3

conn = sqlite3.connect('phraseologisms_with_similarity_v3.db')
cursor = conn.cursor()

cursor.execute("""
    ALTER TABLE phraseologisms 
    ADD COLUMN context_usage TEXT
""")

conn.commit()
conn.close()

print("Колонка context_usage успішно додана!")