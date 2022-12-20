from dataclasses import dataclass
from typing import List, Union


@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    can_access_closed: bool
    can_see_all_posts: bool
    is_closed: Union[bool, None]


@dataclass
class PostAttachment:
    type: str
    url: str


@dataclass
class Post:
    id: int
    text: str
    attachments: List[PostAttachment]
