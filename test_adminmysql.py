import mysql.connector

# Конфигурация для MySQL (порт 3307)
admin_config = {
    'user': 'admin_user',
    'password': 'password123',
    'host': '127.0.0.1',
    'port': 3307,
    'database': 'university_db'
}

def test_admin_permissions():
    try:
        conn = mysql.connector.connect(**admin_config)
        # buffered=True важен для MySQL, чтобы не было ошибки "Unread result"
        cursor = conn.cursor(buffered=True)

        print("--- [MySQL] ТЕСТ АДМИНИСТРАТОРА ---")

        # 1. Чтение таблицы с зарезервированным именем
        cursor.execute("SELECT * FROM `groups` LIMIT 1")
        cursor.fetchall()
        print("1. Чтение таблицы 'groups': УСПЕШНО")

        # 2. Изменение данных
        cursor.execute("UPDATE students SET full_name = 'Админ Админович' WHERE student_id = 1")
        conn.commit()
        print("2. Изменение таблицы 'students': УСПЕШНО")

        # 3. Чтение представления
        cursor.execute("SELECT * FROM vw_student_grades LIMIT 1")
        cursor.fetchall()
        print("3. Чтение View 'vw_student_grades': УСПЕШНО")

    except mysql.connector.Error as err:
        print(f"Ошибка MySQL: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    test_admin_permissions()
