import psycopg2
from psycopg2 import OperationalError, errorcodes

# Общие настройки подключения к Postgres
DB_CONFIG = {
    'dbname': 'university_db',
    'host': '127.0.0.1',
    'port': 5435
}

# Данные пользователей
USERS = {
    'Администратор': {'user': 'user_admin', 'password': 'password123'},
    'Наблюдатель': {'user': 'user_observer', 'password': 'password123'},
    'Оператор': {'user': 'user_operator', 'password': 'password123'}
}


def run_pg_test(role_name, credentials, query, description, should_fail=False):
    """Функция для выполнения теста безопасности в PostgreSQL"""
    print(f"[{role_name}] {description}...", end=" ")
    conn = None
    try:
        # Подключаемся под конкретной ролью
        config = {**DB_CONFIG, **credentials}
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()

        cursor.execute(query)
        if "SELECT" in query.upper():
            cursor.fetchall()
        conn.commit()

        print("✅ УСПЕШНО")
    except Exception as err:
        # В Postgres ошибка прав доступа обычно имеет код '42501'
        if should_fail:
            # Отрезаем лишние детали из сообщения об ошибке для чистоты вывода
            error_msg = str(err).split('\n')[0]
            print(f"❌ ОТКАЗ (Ожидаемо: {error_msg})")
        else:
            print(f"‼️ ОШИБКА (Неожиданно: {err})")
    finally:
        if conn:
            cursor.close()
            conn.close()


def main():
    print("=== ТЕСТИРОВАНИЕ ПРАВ ДОСТУПА POSTGRESQL ===\n")

    # --- ТЕСТ 1: НАБЛЮДАТЕЛЬ ---
    role = 'Наблюдатель'
    creds = USERS[role]
    # Разрешено: смотреть конкретное вью
    run_pg_test(role, creds, "SELECT * FROM vw_student_grades", "Чтение разрешенного представления")
    # Запрещено: смотреть таблицы напрямую
    run_pg_test(role, creds, "SELECT * FROM students", "Чтение таблицы напрямую", should_fail=True)
    # Запрещено: изменять данные
    run_pg_test(role, creds, "UPDATE grades SET grade_value=2", "Попытка изменить данные", should_fail=True)

    print("-" * 60)

    # --- ТЕСТ 2: ОПЕРАТОР ---
    role = 'Оператор'
    creds = USERS[role]
    # Разрешено: смотреть все вью
    run_pg_test(role, creds, "SELECT * FROM vw_student_groups", "Чтение представлений")
    # Разрешено: менять таблицу grades
    run_pg_test(role, creds, "UPDATE grades SET grade_value=5 WHERE grade_id=1", "Изменение таблицы 'grades'")
    # Запрещено: менять таблицу students
    run_pg_test(role, creds, "UPDATE students SET full_name='Error' WHERE student_id=1", "Изменение таблицы 'students'",
                should_fail=True)

    print("-" * 60)

    # --- ТЕСТ 3: АДМИНИСТРАТОР ---
    role = 'Администратор'
    creds = USERS[role]
    # Разрешено всё (используем кавычки для "groups")
    run_pg_test(role, creds, 'SELECT * FROM "groups"', "Чтение любой таблицы")
    run_pg_test(role, creds, "UPDATE students SET full_name='PG Admin Edit' WHERE student_id=1",
                "Изменение любой таблицы")
    run_pg_test(role, creds, "CREATE TEMP TABLE test_auth(id int)", "Создание объектов (админ-функции)")

    print("\n=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")


if __name__ == "__main__":
    main()
