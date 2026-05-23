import sqlite3
import shutil

shutil.copy('phraseologisms_with_similarity_v3.db', 'phraseologisms_similarity_and_syntax.db')

conn = sqlite3.connect('phraseologisms_similarity_and_syntax.db')
cursor = conn.cursor()

cursor.execute("""
    ALTER TABLE phraseologisms
    ADD COLUMN syntax_role TEXT
""")

conn.commit()
conn.close()

print("Копію створено, колонку syntax_role додано!")