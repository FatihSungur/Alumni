import psycopg2

from models.db import get_connection

COLUMNS = "id, user_id, job_posting_id, applied_date"


class JobApplication:
    @staticmethod
    def create(user_id, job_posting_id, applied_date):
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"""
                INSERT INTO job_applications (user_id, job_posting_id, applied_date)
                VALUES (%s, %s, %s)
                RETURNING {COLUMNS}
                """,
                (user_id, job_posting_id, applied_date),
            )
            application = cursor.fetchone()
            connection.commit()
            return application
        except psycopg2.errors.UniqueViolation:
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_all():
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM job_applications ORDER BY id")
        applications = cursor.fetchall()
        cursor.close()
        connection.close()
        return applications

    @staticmethod
    def get_by_id(application_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM job_applications WHERE id = %s", (application_id,))
        application = cursor.fetchone()
        cursor.close()
        connection.close()
        return application

    @staticmethod
    def get_by_user(user_id):
        """One side of the many-to-many: every job this user applied to (joined with job_postings for details)."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT job_applications.id, job_applications.applied_date,
                   job_postings.id AS job_posting_id, job_postings.title, job_postings.company
            FROM job_applications
            JOIN job_postings ON job_postings.id = job_applications.job_posting_id
            WHERE job_applications.user_id = %s
            ORDER BY job_applications.id
            """,
            (user_id,),
        )
        applications = cursor.fetchall()
        cursor.close()
        connection.close()
        return applications

    @staticmethod
    def get_by_job_posting(job_posting_id):
        """Other side of the many-to-many: everyone who applied to this job (joined with users for details)."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT job_applications.id, job_applications.applied_date,
                   users.id AS user_id, users.first_name, users.last_name, users.email
            FROM job_applications
            JOIN users ON users.id = job_applications.user_id
            WHERE job_applications.job_posting_id = %s
            ORDER BY job_applications.id
            """,
            (job_posting_id,),
        )
        applications = cursor.fetchall()
        cursor.close()
        connection.close()
        return applications

    @staticmethod
    def delete(application_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"DELETE FROM job_applications WHERE id = %s RETURNING {COLUMNS}", (application_id,)
        )
        application = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return application
