class ServiceException(Exception):
    def __init__(self, message: str):
        self.message = message


class UserDoesNotExist(ServiceException):
    """User does not exist."""
