import mysql.connector

# Подключаемся под ОГРАНИЧЕННЫМ пользователем
observer_config = {
    'user': 'observer_user',
    'password': 'password123',
    'host': '127.0.0.1',
    'port': 3307,
    'database': 'university_db'
}

def test_observer_permissions():
    try:
        conn = mysql.connector.connect(**observer_config)
        cursor = conn.cursor()

        # 1. Пробуем прочитать разрешенное представление (должно сработать)
        print("--- Тест 1: Чтение vw_student_grades ---")
        cursor.execute("SELECT * FROM vw_student_grades")
        for row in cursor.fetchall():
            print(row)

        # 2. Пробуем прочитать таблицу напрямую (должна быть ошибка)
        print("\n--- Тест 2: Чтение таблицы students напрямую ---")
        try:
            cursor.execute("SELECT * FROM students")
        except mysql.connector.Error as err:
            print(f"Ожидаемый отказ в доступе: {err}")

        # 3. Пробуем изменить данные (должна быть ошибка)
        print("\n--- Тест 3: Попытка изменения данных ---")
        try:
            cursor.execute("UPDATE grades SET grade_value = 5 WHERE grade_id = 1")
        except mysql.connector.Error as err:
            print(f"Ожидаемый отказ в доступе: {err}")

    except mysql.connector.Error as err:
        print(f"Ошибка подключения: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    test_observer_permissions()

