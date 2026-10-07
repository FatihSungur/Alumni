class User:
    _users = []
    _next_id = 1

    def __init__(self, first_name, last_name, graduation_year, email, id=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.graduation_year = graduation_year
        self.email = email

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "graduation_year": self.graduation_year,
            "email": self.email,
        }

    @classmethod
    def create(cls, first_name, last_name, graduation_year, email):
        user = cls(first_name, last_name, graduation_year, email, id=cls._next_id)
        cls._next_id += 1
        cls._users.append(user)
        return user

    @classmethod
    def get_all(cls):
        return cls._users

    @classmethod
    def get_by_id(cls, user_id):
        return next((user for user in cls._users if user.id == user_id), None)

    @classmethod
    def update(cls, user_id, first_name, last_name, graduation_year, email):
        user = cls.get_by_id(user_id)
        if user is None:
            return None
        user.first_name = first_name
        user.last_name = last_name
        user.graduation_year = graduation_year
        user.email = email
        return user

    @classmethod
    def patch(cls, user_id, **fields):
        user = cls.get_by_id(user_id)
        if user is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        return user

    @classmethod
    def delete(cls, user_id):
        user = cls.get_by_id(user_id)
        if user is None:
            return None
        cls._users.remove(user)
        return user
