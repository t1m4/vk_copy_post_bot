class UserServiceException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message


class UserDoesNotExist(UserServiceException):
    """User does not exist."""
