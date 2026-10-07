class Announcement:
    _announcements = []
    _next_id = 1

    def __init__(self, title, content, date, id=None):
        self.id = id
        self.title = title
        self.content = content
        self.date = date

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "date": self.date,
        }

    @classmethod
    def create(cls, title, content, date):
        announcement = cls(title, content, date, id=cls._next_id)
        cls._next_id += 1
        cls._announcements.append(announcement)
        return announcement

    @classmethod
    def get_all(cls):
        return cls._announcements

    @classmethod
    def get_by_id(cls, announcement_id):
        return next(
            (a for a in cls._announcements if a.id == announcement_id), None
        )

    @classmethod
    def update(cls, announcement_id, title, content, date):
        announcement = cls.get_by_id(announcement_id)
        if announcement is None:
            return None
        announcement.title = title
        announcement.content = content
        announcement.date = date
        return announcement

    @classmethod
    def patch(cls, announcement_id, **fields):
        announcement = cls.get_by_id(announcement_id)
        if announcement is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(announcement, key, value)
        return announcement

    @classmethod
    def delete(cls, announcement_id):
        announcement = cls.get_by_id(announcement_id)
        if announcement is None:
            return None
        cls._announcements.remove(announcement)
        return announcement
