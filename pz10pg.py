import psycopg2

# Конфигурация для Postgres (порт 5435 из вашего docker-compose)
config = {
    'dbname': 'university_db',
    'user': 'postgres',
    'password': 'root_password',
    'host': '127.0.0.1',
    'port': 5435
}

def setup_postgres_db():
    conn = None
    try:
        conn = psycopg2.connect(**config)
        conn.autocommit = True  # Для создания ролей вне транзакций
        cursor = conn.cursor()

        # 1. Создание представлений (используем двойные кавычки для "groups")
        views = {
            "vw_student_groups": """
                SELECT s.full_name, g.group_name 
                FROM students s 
                JOIN "groups" g ON s.group_id = g.group_id
            """,
            "vw_subject_teachers": """
                SELECT sub.subject_name, t.full_name as teacher_name 
                FROM subjects sub 
                JOIN teachers t ON sub.teacher_id = t.teacher_id
            """,
            "vw_student_grades": """
                SELECT s.full_name, sub.subject_name, g.grade_value, g.grade_date 
                FROM grades g
                JOIN students s ON g.student_id = s.student_id
                JOIN subjects sub ON g.subject_id = sub.subject_id
            """
        }

        for view_name, query in views.items():
            cursor.execute(f"CREATE OR REPLACE VIEW {view_name} AS {query}")
            print(f"Представление {view_name} создано.")

        # 2. Создание ролей
        # Проверяем существование ролей перед созданием
        roles = ['admin_role', 'observer_role', 'operator_role']
        for role in roles:
            cursor.execute(f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{role}') "
                           f"THEN CREATE ROLE {role}; END IF; END $$;")

        # Даем базовое разрешение на использование схемы public всем ролям
        cursor.execute("GRANT USAGE ON SCHEMA public TO admin_role, observer_role, operator_role")

        # Группа 1: Администраторы (Все права на все таблицы и представления в public)
        cursor.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role")
        cursor.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_role")

        # Группа 2: Наблюдатели (Только SELECT на одно представление)
        cursor.execute("GRANT SELECT ON vw_student_grades TO observer_role")

        # Группа 3: Операторы (Все вью + работа с таблицей grades)
        cursor.execute("GRANT SELECT ON vw_student_groups, vw_subject_teachers, vw_student_grades TO operator_role")
        cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON grades TO operator_role")

        # 3. Создание пользователей (убрали префикс pg_ чтобы избежать ошибки резервирования)
        users = [
            ("user_admin", "admin_role"),
            ("user_observer", "observer_role"),
            ("user_operator", "operator_role")
        ]

        for user, role in users:
            # PostgreSQL не позволяет создавать роли с именами на pg_*
            cursor.execute(f"""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '{user}') THEN 
                        CREATE USER {user} WITH PASSWORD 'password123'; 
                    END IF; 
                END $$;
            """)
            cursor.execute(f"GRANT {role} TO {user}")

        print("Настройка прав в PostgreSQL успешно завершена.")

    except Exception as err:
        print(f"Ошибка: {err}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_postgres_db()
