
class UserProxy:

    def __init__(self, username, password, user=None):
        self.username = username
        self.password = password
        self.user = user


class AuthTestCaseMixin:

    logged_user = None

    def get_user(self):
        raise NotImplementedError

    def login(self, user):
        if self.logged_user:
            self.logout()

        self.authorize(user.username, user.password)
        self.logged_user = user

    def authorize(self, username, password):
        raise NotImplementedError

    def logout(self):
        raise NotImplementedError
