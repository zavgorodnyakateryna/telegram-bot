import sqlite3

conn = sqlite3.connect('phraseologisms.db')
cursor = conn.cursor()


def add_phrase():
    print("\nДодавання нового фразеологізму")

    phrase = input("Фразеологізм: ")
    definition = input("Визначення: ")
    example = input("Приклад вживання: ")
    source = input("Джерело (наприклад: Народне, Шевченко, тощо): ")

    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()

    print("\nКатегорії:")
    for cat in categories:
        print(f"{cat[0]}. {cat[1]}")

    category_id = int(input("\nВведи номер категорії: "))

    cursor.execute('''
                   INSERT INTO phraseologisms
                       (phrase, definition, example, source, category_id)
                   VALUES (?, ?, ?, ?, ?)
                   ''', (phrase, definition, example, source, category_id))

    conn.commit()
    print("Фразеологізм успішно додано!")

while True:
    add_phrase()
    if input("\nДодати ще один? (y): ").lower() != 'y':
        break

print("Готово! База наповнена.")
conn.close()