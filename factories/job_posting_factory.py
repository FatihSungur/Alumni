from faker import Faker

fake = Faker()


class JobPostingFactory:
    @staticmethod
    def create(posted_by):
        return {
            "title": fake.job(),
            "company": fake.company(),
            "description": fake.paragraph(nb_sentences=4),
            "location": fake.city(),
            "posted_by": posted_by,
            "posted_date": fake.date_this_year().isoformat(),
        }
