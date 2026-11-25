from models.db import get_connection

COLUMNS = "id, title, company, description, location, posted_by, posted_date, status"


class JobPosting:
    MAX_TITLE_LENGTH = 120

    @staticmethod
    def validate(title, company):
        """Field rules for creating a job posting (see DDD.md). Returns a list of
        error messages — empty means the data is valid."""
        errors = []
        if not title:
            errors.append("title required")
        elif len(title) > JobPosting.MAX_TITLE_LENGTH:
            errors.append(f"title must be at most {JobPosting.MAX_TITLE_LENGTH} characters")
        if not company:
            errors.append("company required")
        return errors

    @staticmethod
    def create(title, company, description, location, posted_by, posted_date):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO job_postings (title, company, description, location, posted_by, posted_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
            RETURNING {COLUMNS}
            """,
            (title, company, description, location, posted_by, posted_date),
        )
        job_posting = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return job_posting

    @staticmethod
    def get_all():
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM job_postings ORDER BY id")
        job_postings = cursor.fetchall()
        cursor.close()
        connection.close()
        return job_postings

    @staticmethod
    def get_approved():
        """What guests/students/alumni see — pending postings are hidden
        until a moderator or admin approves them."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM job_postings WHERE status = 'approved' ORDER BY id")
        job_postings = cursor.fetchall()
        cursor.close()
        connection.close()
        return job_postings

    @staticmethod
    def get_pending():
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM job_postings WHERE status = 'pending' ORDER BY id")
        job_postings = cursor.fetchall()
        cursor.close()
        connection.close()
        return job_postings

    @staticmethod
    def approve(job_posting_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE job_postings SET status = 'approved' WHERE id = %s RETURNING {COLUMNS}",
            (job_posting_id,),
        )
        job_posting = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return job_posting

    @staticmethod
    def get_by_id(job_posting_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {COLUMNS} FROM job_postings WHERE id = %s", (job_posting_id,))
        job_posting = cursor.fetchone()
        cursor.close()
        connection.close()
        return job_posting

    @staticmethod
    def get_by_user(user_id):
        """The one-to-many relationship in action: every job posting made by a given user."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT {COLUMNS} FROM job_postings WHERE posted_by = %s ORDER BY id",
            (user_id,),
        )
        job_postings = cursor.fetchall()
        cursor.close()
        connection.close()
        return job_postings

    @staticmethod
    def update(job_posting_id, title, company, description, location, posted_date):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"""
            UPDATE job_postings
            SET title = %s, company = %s, description = %s, location = %s, posted_date = %s
            WHERE id = %s
            RETURNING {COLUMNS}
            """,
            (title, company, description, location, posted_date, job_posting_id),
        )
        job_posting = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return job_posting

    @staticmethod
    def patch(job_posting_id, **fields):
        fields = {key: value for key, value in fields.items() if value is not None}
        if not fields:
            return JobPosting.get_by_id(job_posting_id)

        set_clause = ", ".join(f"{key} = %s" for key in fields)
        values = list(fields.values()) + [job_posting_id]

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE job_postings SET {set_clause} WHERE id = %s RETURNING {COLUMNS}",
            values,
        )
        job_posting = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return job_posting

    @staticmethod
    def delete(job_posting_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            f"DELETE FROM job_postings WHERE id = %s RETURNING {COLUMNS}", (job_posting_id,)
        )
        job_posting = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return job_posting
