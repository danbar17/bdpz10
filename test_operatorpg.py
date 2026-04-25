import psycopg2

# Конфигурация для оператора (Postgres порт 5435)
operator_config = {
    'dbname': 'university_db',
    'user': 'user_operator',
    'password': 'password123',
    'host': '127.0.0.1',
    'port': 5435
}

def test_pg_operator_permissions():
    conn = None
    try:
        conn = psycopg2.connect(**operator_config)
        cursor = conn.cursor()

        print("--- [PostgreSQL] ТЕСТ ОПЕРАТОРА ---")

        # 1. Просмотр всех представлений
        print("1. Доступ к представлениям:")
        views = ["vw_student_groups", "vw_subject_teachers", "vw_student_grades"]
        for view in views:
            try:
                cursor.execute(f"SELECT * FROM {view} LIMIT 1")
                cursor.fetchall()
                print(f"   - {view}: ДОСТУПЕН")
            except Exception as e:
                print(f"   - {view}: ОШИБКА ({e})")
                conn.rollback()

        # 2. Изменение данных в разрешенной таблице (grades)
        print("\n2. Изменение данных в 'grades':", end=" ")
        try:
            cursor.execute("UPDATE grades SET grade_value = 4 WHERE grade_id = 1")
            conn.commit() # Здесь фиксируем изменения
            print("УСПЕШНО (разрешено)")
        except Exception as e:
            print(f"ОШИБКА ({e})")
            conn.rollback()

        # 3. Попытка изменить данные в защищенной таблице (students)
        print("3. Изменение данных в 'students':", end=" ")
        try:
            cursor.execute("UPDATE students SET full_name = 'Новое Имя' WHERE student_id = 1")
            conn.commit()
            print("УСПЕШНО (ошибка, доступ должен быть закрыт)")
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
    test_pg_operator_permissions()
