import os
import random

import psycopg2

from factories.announcement_factory import AnnouncementFactory
from factories.job_application_factory import JobApplicationFactory
from factories.job_posting_factory import JobPostingFactory
from factories.user_factory import UserFactory

DATABASE_URL = os.environ.get("DATABASE_URL")


def seed_users(cursor, count=10):
    for _ in range(count):
        user = UserFactory.create()
        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, graduation_year, email)
            VALUES (%s, %s, %s, %s)
            """,
            (user["first_name"], user["last_name"], user["graduation_year"], user["email"]),
        )


def seed_announcements(cursor, count=5):
    for _ in range(count):
        announcement = AnnouncementFactory.create()
        cursor.execute(
            """
            INSERT INTO announcements (title, content, date)
            VALUES (%s, %s, %s)
            """,
            (announcement["title"], announcement["content"], announcement["date"]),
        )


def seed_job_postings(cursor, user_ids, count=8):
    for _ in range(count):
        posted_by = random.choice(user_ids)
        job_posting = JobPostingFactory.create(posted_by)
        cursor.execute(
            """
            INSERT INTO job_postings (title, company, description, location, posted_by, posted_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                job_posting["title"],
                job_posting["company"],
                job_posting["description"],
                job_posting["location"],
                job_posting["posted_by"],
                job_posting["posted_date"],
            ),
        )


def seed_job_applications(cursor, user_ids, job_posting_ids, count=10):
    for _ in range(count):
        user_id = random.choice(user_ids)
        job_posting_id = random.choice(job_posting_ids)
        application = JobApplicationFactory.create(user_id, job_posting_id)
        cursor.execute(
            """
            INSERT INTO job_applications (user_id, job_posting_id, applied_date)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, job_posting_id) DO NOTHING
            """,
            (
                application["user_id"],
                application["job_posting_id"],
                application["applied_date"],
            ),
        )


def main():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    seed_users(cursor, count=10)
    seed_announcements(cursor, count=5)
    connection.commit()

    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    seed_job_postings(cursor, user_ids, count=8)
    connection.commit()

    cursor.execute("SELECT id FROM job_postings")
    job_posting_ids = [row[0] for row in cursor.fetchall()]

    seed_job_applications(cursor, user_ids, job_posting_ids, count=10)
    connection.commit()

    cursor.close()
    connection.close()

    print("Seeded 10 users, 5 announcements, 8 job postings, up to 10 job applications.")


if __name__ == "__main__":
    main()
