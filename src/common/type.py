# archive types
from enum import Enum, StrEnum
from dataclasses import dataclass, field


class Category(Enum):
    ARTIFACT = "artifact"
    BOOK = "book"
    WEAPON = "weapon"


@dataclass
class Volume:
    """Representing a volume in a book collection"""

    description: str
    text: str


@dataclass
class BookCollection:
    """Representing a book collection archive"""

    title: str
    location: str
    volumes: list[Volume]


@dataclass
class QuestBook:
    """Representing a book of other type, listed under quest items"""

    title: str
    location: str
    text: str


class BookCategory(StrEnum):
    """Enum types for books: book collection, quest/other"""

    collection = "collection"
    quest = "quest"


@dataclass
class BookArchive:
    book_collections: list[BookCollection] = field(default_factory=list)
    quest_books: list[QuestBook] = field(default_factory=list)

    def count(self):
        return len(self.book_collections) + len(self.quest_books)
