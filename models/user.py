import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash

from models.db import get_connection

COLUMNS = "id, first_name, last_name, graduation_year, email, role, staff_role, status, requested_role"
ROLES = ("alumni", "student")
STAFF_ROLES = ("admin", "moderator")
PERMISSIONS = (
    "approve_users",
    "manage_users",
    "add_users",
    "approve_job_postings",
    "approve_announcements",
    "approve_role_changes",
)


class User:
    @staticmethod
    def get_by_email(email):
        """Includes password_hash — unlike COLUMNS, only for internal use by login."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT {COLUMNS}, password_hash FROM users WHERE email = %s", (email,)
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def verify_password(user, password):
        if user is None or not user["password_hash"]:
            return False
        return check_password_hash(user["password_hash"], password)

    @staticmethod
    def validate_registration(first_name, last_name, email, graduation_year, role, password):
        errors = []
        if not first_name:
            errors.append("first name required")
        if not last_name:
            errors.append("last name required")
        if not email:
            errors.append("email required")
        if not graduation_year:
            errors.append("graduation year required")
        if role not in ROLES:
            errors.append("role must be alumni or student")
        if not password or len(password) < 6:
            errors.append("password must be at least 6 characters")
        return errors

    @staticmethod
    def register(first_name, last_name, graduation_year, email, role, password):
        password_hash = generate_password_hash(password)
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"""
                INSERT INTO users (first_name, last_name, graduation_year, email, role, password_hash, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                RETURNING {COLUMNS}
                """,
                (first_name, last_name, graduation_year, email, role, password_hash),
            )
            user = cursor.fetchone()
            connection.commit()
        except psycopg2.errors.UniqueViolation:
            connection.rollback()
            user = None
        finally:
            cursor.close()
            connection.close()
        return user

    @staticmethod
    def validate_roles(role, staff_role):
        errors = []
        if role not in ROLES:
            errors.append("role must be alumni or student")
        if staff_role and staff_role not in STAFF_ROLES:
            errors.append("staff role must be empty, admin, or moderator")
        return errors

    @staticmethod
    def set_roles(user_id, role, staff_role):
        """Admin-only: change a user's base role and/or staff role. staff_role
        may be None (removes admin/moderator privileges)."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            UPDATE users
            SET role = %s, staff_role = %s
            WHERE id = %s
            RETURNING {COLUMNS}
            """,
            (role, staff_role, user_id),
        )
        user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def get_pending():
        """Registrations awaiting approval."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM users WHERE status = 'pending' ORDER BY id")
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return users

    @staticmethod
    def approve(user_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE users SET status = 'approved' WHERE id = %s RETURNING {COLUMNS}",
            (user_id,),
        )
        user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def get_permissions(user_id):
        """The specific admin-panel features a moderator has been granted
        (see moderator_permissions, migrations/005...). Meaningless for an
        'admin' staff_role, which always has every permission implicitly."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT permission FROM moderator_permissions WHERE user_id = %s ORDER BY permission",
            (user_id,),
        )
        permissions = [row["permission"] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return permissions

    @staticmethod
    def set_permissions(user_id, permissions):
        """Replaces this user's full permission set with the given list
        (only meaningful while staff_role = 'moderator' — see DDD.md)."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM moderator_permissions WHERE user_id = %s", (user_id,))
        for permission in permissions:
            cursor.execute(
                "INSERT INTO moderator_permissions (user_id, permission) VALUES (%s, %s)",
                (user_id, permission),
            )
        connection.commit()
        cursor.close()
        connection.close()

    @staticmethod
    def request_role_change(user_id, requested_role):
        """A student asking to become alumni (or vice versa) — stays as
        their current role, functionally, until a staff member approves."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE users SET requested_role = %s WHERE id = %s RETURNING {COLUMNS}",
            (requested_role, user_id),
        )
        user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def get_pending_role_changes():
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT {COLUMNS} FROM users WHERE requested_role IS NOT NULL ORDER BY id"
        )
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return users

    @staticmethod
    def approve_role_change(user_id):
        """Promotes role to whatever was requested, then clears the request."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            UPDATE users
            SET role = requested_role, requested_role = NULL
            WHERE id = %s
            RETURNING {COLUMNS}
            """,
            (user_id,),
        )
        user = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return user

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
    def get_approved():
        """The public alumni directory — pending registrations are hidden
        until an admin/permitted moderator approves them."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM users WHERE status = 'approved' ORDER BY id")
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
