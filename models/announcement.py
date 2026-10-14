from models.db import get_connection

COLUMNS = "id, title, content, date"


class Announcement:
    @staticmethod
    def create(title, content, date):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO announcements (title, content, date)
            VALUES (%s, %s, %s)
            RETURNING {COLUMNS}
            """,
            (title, content, date),
        )
        announcement = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return announcement

    @staticmethod
    def get_all():
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM announcements ORDER BY id")
        announcements = cursor.fetchall()
        cursor.close()
        connection.close()
        return announcements

    @staticmethod
    def get_by_id(announcement_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM announcements WHERE id = %s", (announcement_id,))
        announcement = cursor.fetchone()
        cursor.close()
        connection.close()
        return announcement

    @staticmethod
    def update(announcement_id, title, content, date):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            UPDATE announcements
            SET title = %s, content = %s, date = %s
            WHERE id = %s
            RETURNING {COLUMNS}
            """,
            (title, content, date, announcement_id),
        )
        announcement = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return announcement

    @staticmethod
    def patch(announcement_id, **fields):
        fields = {key: value for key, value in fields.items() if value is not None}
        if not fields:
            return Announcement.get_by_id(announcement_id)

        set_clause = ", ".join(f"{key} = %s" for key in fields)
        values = list(fields.values()) + [announcement_id]

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE announcements SET {set_clause} WHERE id = %s RETURNING {COLUMNS}",
            values,
        )
        announcement = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return announcement

    @staticmethod
    def delete(announcement_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"DELETE FROM announcements WHERE id = %s RETURNING {COLUMNS}", (announcement_id,)
        )
        announcement = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return announcement
