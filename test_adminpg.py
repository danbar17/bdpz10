import psycopg2

# Конфигурация для администратора (Postgres порт 5435)
admin_config = {
    'dbname': 'university_db',
    'user': 'user_admin',
    'password': 'password123',
    'host': '127.0.0.1',
    'port': 5435
}

def test_pg_admin_permissions():
    conn = None
    try:
        conn = psycopg2.connect(**admin_config)
        cursor = conn.cursor()

        print("--- [PostgreSQL] ТЕСТ АДМИНИСТРАТОРА ---")

        # 1. Чтение таблицы с зарезервированным именем (используем двойные кавычки)
        print("1. Чтение системной таблицы \"groups\":", end=" ")
        cursor.execute('SELECT * FROM "groups" LIMIT 1')
        cursor.fetchall()
        print("УСПЕШНО")

        # 2. Изменение данных в любой таблице (например, students)
        print("2. Изменение данных в 'students':", end=" ")
        try:
            cursor.execute("UPDATE students SET full_name = 'Админ Постгресович' WHERE student_id = 1")
            conn.commit()
            print("УСПЕШНО")
        except Exception as e:
            print(f"ОШИБКА: {e}")
            conn.rollback()

        # 3. Полный доступ к представлениям
        print("3. Чтение представления 'vw_subject_teachers':", end=" ")
        cursor.execute("SELECT * FROM vw_subject_teachers LIMIT 1")
        cursor.fetchall()
        print("УСПЕШНО")

        # 4. Проверка прав на удаление
        print("4. Тест прав на DELETE в 'grades':", end=" ")
        try:
            cursor.execute("DELETE FROM grades WHERE grade_id = 999")
            conn.commit()
            print("УСПЕШНО (права подтверждены)")
        except Exception as e:
            print(f"ОШИБКА: {e}")
            conn.rollback()

    except Exception as err:
        print(f"Ошибка подключения: {err}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    test_pg_admin_permissions()
