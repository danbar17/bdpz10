import mysql.connector
from mysql.connector import errorcode

# Общие настройки подключения
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'database': 'university_db'
}

# Данные пользователей
USERS = {
    'Администратор': {'user': 'admin_user', 'password': 'password123'},
    'Наблюдатель': {'user': 'observer_user', 'password': 'password123'},
    'Оператор': {'user': 'operator_user', 'password': 'password123'}
}


def run_test(role_name, credentials, query, description, should_fail=False):
    """Функция для выполнения одного теста безопасности"""
    print(f"[{role_name}] {description}...", end=" ")
    conn = None
    try:
        # Смешиваем общие настройки с учетными данными конкретной роли
        config = {**DB_CONFIG, **credentials}
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(buffered=True)

        cursor.execute(query)
        if "SELECT" in query.upper():
            cursor.fetchall()
        conn.commit()

        print("✅ УСПЕШНО")
    except mysql.connector.Error as err:
        if should_fail:
            print(f"❌ ОТКАЗ (Ожидаемо: {err.msg})")
        else:
            print(f"‼️ ОШИБКА (Неожиданно: {err.msg})")
    finally:
        if conn and conn.is_connected():
            conn.close()


def main():
    print("=== ТЕСТИРОВАНИЕ ПРАВ ДОСТУПА MYSQL ===\n")

    # --- ТЕСТ 1: НАБЛЮДАТЕЛЬ ---
    role = 'Наблюдатель'
    creds = USERS[role]
    # Разрешено: смотреть конкретное вью
    run_test(role, creds, "SELECT * FROM vw_student_grades", "Чтение разрешенного представления")
    # Запрещено: смотреть таблицы напрямую
    run_test(role, creds, "SELECT * FROM students", "Чтение таблицы напрямую", should_fail=True)
    # Запрещено: изменять данные
    run_test(role, creds, "UPDATE grades SET grade_value=2", "Попытка изменить данные", should_fail=True)

    print("-" * 50)

    # --- ТЕСТ 2: ОПЕРАТОР ---
    role = 'Оператор'
    creds = USERS[role]
    # Разрешено: смотреть все вью
    run_test(role, creds, "SELECT * FROM vw_student_groups", "Чтение представлений")
    # Разрешено: менять таблицу grades
    run_test(role, creds, "UPDATE grades SET grade_value=5 WHERE grade_id=1", "Изменение таблицы 'grades'")
    # Запрещено: менять таблицу students
    run_test(role, creds, "UPDATE students SET full_name='Error' WHERE student_id=1", "Изменение таблицы 'students'",
             should_fail=True)

    print("-" * 50)

    # --- ТЕСТ 3: АДМИНИСТРАТОР ---
    role = 'Администратор'
    creds = USERS[role]
    # Разрешено всё
    run_test(role, creds, "SELECT * FROM `groups`", "Чтение любой таблицы")
    run_test(role, creds, "UPDATE students SET full_name='Admin Edit' WHERE student_id=1", "Изменение любой таблицы")
    run_test(role, creds, "DROP VIEW IF EXISTS vw_test_delete", "Удаление объектов (админ-функции)")

    print("\n=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")


if __name__ == "__main__":
    main()
