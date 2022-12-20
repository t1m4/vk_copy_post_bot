from typing import Dict, Union


class VKAPIException(Exception):
    def __init__(self, message: Union[str, Dict], status_code: Union[int, None] = None):
        self.status_code = status_code
        self.error_message = message

    def __str__(self):
        if self.status_code:
            return "{} {}".format(self.status_code, self.error_message)
        else:
            return "{}".format(self.error_message)
