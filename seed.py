import os

import psycopg2

from factories.announcement_factory import AnnouncementFactory
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


def main():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    seed_users(cursor, count=10)
    seed_announcements(cursor, count=5)

    connection.commit()
    cursor.close()
    connection.close()

    print("Seeded 10 users and 5 announcements.")


if __name__ == "__main__":
    main()
