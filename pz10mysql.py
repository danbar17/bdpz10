import mysql.connector

# Конфигурация подключения (используем порт 3307, как в вашем docker-compose)
config = {
    'user': 'root',
    'password': 'root_password',
    'host': '127.0.0.1',
    'port': 3307,
    'database': 'university_db'
}

def setup_university_db():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # 1. Создание представлений
        # Используем обратные кавычки `groups`, так как это зарезервированное слово
        views = {
            "vw_student_groups": """
                SELECT s.full_name, g.group_name 
                FROM students s 
                JOIN `groups` g ON s.group_id = g.group_id
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

        # 2. Создание ролей (групп пользователей)
        # В MySQL роли ведут себя как группы прав
        cursor.execute("CREATE ROLE IF NOT EXISTS 'admin_role', 'observer_role', 'operator_role'")

        # Группа 1: Администраторы (Полный доступ)
        cursor.execute("GRANT ALL PRIVILEGES ON university_db.* TO 'admin_role'")

        # Группа 2: Наблюдатели (Только одно представление)
        cursor.execute("GRANT SELECT ON university_db.vw_student_grades TO 'observer_role'")

        # Группа 3: Операторы (Все представления + изменение таблицы grades)
        cursor.execute("GRANT SELECT ON university_db.vw_student_groups TO 'operator_role'")
        cursor.execute("GRANT SELECT ON university_db.vw_subject_teachers TO 'operator_role'")
        cursor.execute("GRANT SELECT ON university_db.vw_student_grades TO 'operator_role'")
        cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON university_db.grades TO 'operator_role'")

        # 3. Пример создания конкретных пользователей и назначения им ролей
        users = [
            ("admin_user", "admin_role"),
            ("observer_user", "observer_role"),
            ("operator_user", "operator_role")
        ]

        for username, role in users:
            cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY 'password123'")
            cursor.execute(f"GRANT '{role}' TO '{username}'@'%'")
            # Делаем роль активной по умолчанию для пользователя
            cursor.execute(f"SET DEFAULT ROLE '{role}' TO '{username}'@'%'")

        conn.commit()
        print("Права доступа и пользователи успешно настроены.")

    except mysql.connector.Error as err:
        print(f"Ошибка: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_university_db()
