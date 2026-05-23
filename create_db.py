import sqlite3

conn = sqlite3.connect('phraseologisms.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS phraseologisms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase TEXT NOT NULL,
    definition TEXT NOT NULL,
    example TEXT,
    source TEXT,
    category_id INTEGER,

    FOREIGN KEY (category_id) REFERENCES categories(id)
)
''')

categories = [
    'Душа', 'Серце', 'Голова', 'Думка',
    'Кров', 'Дух', 'Памʼять',
    'Розум', 'Совість'
]

for cat in categories:
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

cursor.execute("SELECT MAX(id) FROM categories")
max_id = cursor.fetchone()[0] or 0

cursor.execute("""
    UPDATE sqlite_sequence 
    SET seq = ? 
    WHERE name = 'categories'
""", (max_id,))

conn.commit()

print("База даних успішно створена!")
print("Файл бази: phraseologisms.db")
print(f"Кількість категорій: {max_id}")

cursor.execute("SELECT id, name FROM categories ORDER BY id")
print("\nКатегорії:")
for row in cursor.fetchall():
    print(f"{row[0]}. {row[1]}")

conn.close()