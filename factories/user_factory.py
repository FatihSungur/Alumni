from faker import Faker

fake = Faker()


class UserFactory:
    @staticmethod
    def create():
        return {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "graduation_year": fake.random_int(min=2015, max=2026),
            "email": fake.unique.email(),
        }
