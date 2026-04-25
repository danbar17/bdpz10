import mysql.connector

# Конфигурация для оператора (MySQL)
operator_config = {
    'user': 'operator_user',
    'password': 'password123',
    'host': '127.0.0.1',
    'port': 3307,
    'database': 'university_db'
}

def test_operator_permissions():
    try:
        conn = mysql.connector.connect(**operator_config)
        # Добавляем buffered=True, чтобы курсор сам вычитывал данные из буфера
        cursor = conn.cursor(buffered=True)

        # 1. Просмотр всех представлений
        print("--- Тест 1: Проверка доступности всех View ---")
        views = ["vw_student_groups", "vw_subject_teachers", "vw_student_grades"]
        for view in views:
            cursor.execute(f"SELECT * FROM {view} LIMIT 1")
            # Обязательно "вычитываем" результат, чтобы очистить канал
            cursor.fetchall()
            print(f"Доступ к {view}: Успешно")

        # 2. Изменение данных в разрешенной таблице (grades)
        print("\n--- Тест 2: Попытка изменения таблицы 'grades' ---")
        try:
            cursor.execute("UPDATE grades SET grade_value = 5 WHERE grade_id = 1")
            conn.commit()
            print("Обновление в 'grades': Успешно (разрешено)")
        except mysql.connector.Error as err:
            print(f"Ошибка в 'grades': {err}")

        # 3. Попытка изменения данных в запрещенной таблице (students)
        print("\n--- Тест 3: Попытка изменения таблицы 'students' ---")
        try:
            cursor.execute("UPDATE students SET full_name = 'Взломщик' WHERE student_id = 1")
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Ожидаемый отказ в доступе к 'students': {err}")

    except mysql.connector.Error as err:
        print(f"Ошибка подключения: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    test_operator_permissions()
