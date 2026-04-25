import psycopg2

# Конфигурация для Postgres (порт 5435)
observer_config = {
    'dbname': 'university_db',
    'user': 'user_observer',
    'password': 'password123',
    'host': '127.0.0.1',
    'port': 5435
}

def test_pg_observer_permissions():
    conn = None
    try:
        # Подключаемся под ОГРАНИЧЕННЫМ пользователем
        conn = psycopg2.connect(**observer_config)
        cursor = conn.cursor()

        print("--- [PostgreSQL] ТЕСТ НАБЛЮДАТЕЛЯ ---")

        # 1. Пробуем прочитать разрешенное представление
        print("1. Чтение vw_student_grades:", end=" ")
        try:
            cursor.execute("SELECT * FROM vw_student_grades LIMIT 1")
            cursor.fetchall()
            print("УСПЕШНО")
        except Exception as e:
            print(f"ОШИБКА: {e}")
            conn.rollback() # Откатываем транзакцию после ошибки

        # 2. Пробуем прочитать таблицу напрямую (запрещено)
        print("2. Чтение таблицы 'students' напрямую:", end=" ")
        try:
            cursor.execute("SELECT * FROM students LIMIT 1")
            cursor.fetchall()
            print("УСПЕШНО (странно, должно быть запрещено)")
        except Exception as e:
            print("ОТКАЗ В ДОСТУПЕ (норма)")
            conn.rollback()

        # 3. Попытка изменить данные (запрещено)
        print("3. Попытка UPDATE в таблице 'grades':", end=" ")
        try:
            cursor.execute("UPDATE grades SET grade_value = 5 WHERE grade_id = 1")
            conn.commit()
            print("УСПЕШНО (странно, должно быть запрещено)")
        except Exception as e:
            print("ОТКАЗ В ДОСТУПЕ (норма)")
            conn.rollback()

    except Exception as err:
        print(f"Ошибка подключения: {err}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    test_pg_observer_permissions()
