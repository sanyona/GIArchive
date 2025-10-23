BASE_LINK = "https://genshin-impact.fandom.com"

ARTIFACT = "https://genshin-impact.fandom.com/wiki/Artifact/Sets"

WEAPON = "https://genshin-impact.fandom.com/wiki/Weapon/List"

BOOK = "https://genshin-impact.fandom.com/wiki/Book"

links2html_mapping = {  # TODO replace with enum
    "artifact": ARTIFACT,
    "weapon": WEAPON,
    "book": BOOK,
}


# for book scraping (section header)
BOOK_COL_ID = "List_of_Book_Collections"
OTHER_BOOK_ID = "Other_Books"
