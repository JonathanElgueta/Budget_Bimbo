class User:
    def __init__(self, user_id, username, password, fullname=""):
        self.id = user_id
        self.email = username
        self.password = password
        self.fullname = fullname
