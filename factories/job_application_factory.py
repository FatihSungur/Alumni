from faker import Faker

fake = Faker()


class JobApplicationFactory:
    @staticmethod
    def create(user_id, job_posting_id):
        return {
            "user_id": user_id,
            "job_posting_id": job_posting_id,
            "applied_date": fake.date_this_year().isoformat(),
        }
