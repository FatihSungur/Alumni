from faker import Faker

fake = Faker()


class AnnouncementFactory:
    @staticmethod
    def create():
        return {
            "title": fake.sentence(nb_words=6),
            "content": fake.paragraph(nb_sentences=3),
            "date": fake.date_this_year().isoformat(),
        }
