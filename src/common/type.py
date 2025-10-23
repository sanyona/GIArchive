# archive types
from dataclasses import asdict, dataclass, field
from enum import Enum, StrEnum


class Category(Enum):
    ARTIFACT = "artifact"
    BOOK = "book"
    WEAPON = "weapon"


# artifact type
@dataclass
class Artifact:
    """Contain info about a single piece of an artifact"""

    name: str
    description: str
    text: str

    def __str__(self) -> str:
        """User-friendly string for printing/logging."""
        return (
            f"Artifact: {self.name}\n"
            f"  Description: {self.description}\n"
            f"  Text:\n{self.text}"
        )


@dataclass
class ArtifactSet:
    name: str
    artifacts: list[Artifact]

    def __str__(self) -> str:
        """User-friendly string for printing/logging."""
        header = f"Artifact Set: {self.name} ({len(self.artifacts)} items)"
        body = "\n".join(
            f"{idx+1}. {str(artifact)}" for idx, artifact in enumerate(self.artifacts)
        )
        return f"{header}\n{'-' * len(header)}\n{body}"

    def to_dict(self):
        return asdict(self)


# book types


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
