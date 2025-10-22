from enum import Enum
from dataclasses import dataclass

class Category(Enum):
    ARTIFACT = "artifact"
    BOOK = "book"
    WEAPON = "weapon"

@dataclass
class Volume:
    """Representing a volume in a book collection
    """
    description: str
    text: str
@dataclass
class BookCollection:
    """Representing a book collection archive
    """
    title: str
    volumes: list[Volume] 