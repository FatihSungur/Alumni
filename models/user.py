from models.db import get_connection

COLUMNS = "id, first_name, last_name, graduation_year, email"


class User:
    @staticmethod
    def create(first_name, last_name, graduation_year, email):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO users (first_name, last_name, graduation_year, email)
            VALUES (%s, %s, %s, %s)
            RETURNING {COLUMNS}
            """,
            (first_name, last_name, graduation_year, email),
        )
        user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def get_all():
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM users ORDER BY id")
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return users

    @staticmethod
    def get_by_id(user_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def update(user_id, first_name, last_name, graduation_year, email):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            UPDATE users
            SET first_name = %s, last_name = %s, graduation_year = %s, email = %s
            WHERE id = %s
            RETURNING {COLUMNS}
            """,
            (first_name, last_name, graduation_year, email, user_id),
        )
        user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def patch(user_id, **fields):
        fields = {key: value for key, value in fields.items() if value is not None}
        if not fields:
            return User.get_by_id(user_id)

        set_clause = ", ".join(f"{key} = %s" for key in fields)
        values = list(fields.values()) + [user_id]

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE users SET {set_clause} WHERE id = %s RETURNING {COLUMNS}",
            values,
        )
        user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def delete(user_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM users WHERE id = %s RETURNING {COLUMNS}", (user_id,))
        user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return user
