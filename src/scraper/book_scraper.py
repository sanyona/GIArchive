import copy
import json
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, PageElement

from src.common.type import (
    BookArchive,
    BookCategory,
    BookCollection,
    Category,
    QuestBook,
    Volume,
)
from src.common.archives import JSON_DIR, LINKS_DIR
from src.scraper.base import Scraper
from src.util.file import dump_to_json
from src.util.logger import get_logger
from src.util.txt import clean_text
from src.util.url import extract_slug


class BookScraper(Scraper):
    """Scrapes book links from `links/book.json `"""

    def __init__(self, verbose=False):
        self.logger = get_logger("BookScraper", verbose=verbose)

    def _scrape_location(self, soup: BeautifulSoup) -> str:
        """Scrape location info from a books wiki page

        :param soup: _description_
        :return: _description_
        """
        loc_container = soup.find(
            "div",
            class_="pi-item pi-data pi-item-spacing pi-border-color",
            attrs={"data-source": "region_location"},
        )

        if loc_container:
            location = loc_container.find("div", class_="pi-data-value").get_text(
                " ", strip=True
            )
        else:
            location = ""
        return location

    def _scrape_collection(self, links: list[str]) -> dict[str, BookCollection]:
        result = {}
        for link in links:
            self.logger.debug(f"Crawling {link}")
            html = self.get_page(link)
            soup = BeautifulSoup(html, "html.parser")

            title: str = extract_slug(link)

            volumes: list[Volume] = []
            # TODO, load volume count from table?
            for h2 in soup.find_all("h2"):
                # Get headline text (ignore edit links)
                headline_span = h2.find("span", class_="mw-headline")
                if not headline_span:
                    continue
                h2_text = headline_span.get_text(strip=True)

                # irminsul'ed books
                if "version" in h2_text.lower():
                    # get all h3 after this before next h2
                    # iterate through h3
                    h3_groups = []

                    # walk siblings after this h2
                    group = []
                    for elem in h2.find_next_siblings():
                        # stop when next <h2> appears
                        if elem.name == "h2":
                            h3_groups.append(copy.deepcopy(group))
                            break
                        if elem.name == "h3":
                            # stop and start a new list
                            if len(group) > 1:
                                h3_groups.append(copy.deepcopy(group))
                            group = []
                            group.append(elem)
                        else:
                            group.append(elem)

                    for group in h3_groups:
                        texts, description = [], ""
                        # self.logger.debug("group")
                        for elem in group:
                            if elem.name == "div":
                                desc_el = elem.find("div", class_="description-content")
                                if desc_el:
                                    description = desc_el.get_text(strip=True)
                                else:
                                    self.logger.warning(
                                        f"no description found for {link} {h2_text}"
                                    )
                            elif elem.name == "p":
                                texts.append(elem.get_text(separator=" ", strip=True))
                        print(description, texts)
                        volume = Volume(description=description, text="\n".join(texts))
                        volumes.append(volume)
                # regular books
                elif "vol" in h2_text.lower():
                    texts = []
                    description = ""
                    for elem in h2.find_next_siblings():
                        if elem.name == "h2":  # stop when it's not <p>/<div>
                            break
                        # extract descriptions
                        if elem.name == "div" and "description-wrapper" in elem.get(
                            "class", []
                        ):
                            desc_el = elem.find("div", class_="description-content")
                            if desc_el:
                                description = desc_el.get_text(strip=True)
                            else:
                                self.logger.warning(
                                    f"no description found for {link} {h2_text}"
                                )

                        if elem.name == "p":
                            texts.append(elem.get_text(separator=" ", strip=True))

                    volume = Volume(
                        description=description, text=clean_text("\n".join(texts))
                    )
                    volumes.append(volume)
                else:
                    continue

            book = BookCollection(
                title=title, location=self._scrape_location(soup), volumes=volumes
            )
            result[title] = book
        return result

    def _scrape_quest(self, links: list[str]) -> dict[str, QuestBook]:
        """Scraping logic for books under Other Books table (quest books)

        :param links: _description_
        :raises ValueError: _description_
        :return: _description_
        """
        result = {}
        for link in links:
            self.logger.debug(f"Crawling {link}")
            html = self.get_page(link)
            soup = BeautifulSoup(html, "html.parser")

            title = extract_slug(link)
            # Find the <span> with id="Text"
            text_heading = soup.find("span", id="Text")
            lore_heading = soup.find("span", id="Lore")
            if not text_heading and not lore_heading:

                self.logger.error(
                    f"Text/Lore section not found. Page {link} may not be a conventional book"
                )
                continue
            heading_to_use = text_heading or lore_heading

            # 2. Find the parent <h2> to locate the section start
            text_h2 = heading_to_use.find_parent("h2")

            # 3. Collect everything until the next <h2> (artifact piece)
            texts = []
            for sib in text_h2.find_next_siblings():
                if sib.name == "h2":  # stop when it's not <p>
                    break
                if sib.name == "p":
                    texts.append(sib.get_text(separator=" ", strip=True))

            book = QuestBook(
                title=title,
                location=self._scrape_location(soup),
                text=clean_text("\n".join(texts)),
            )
            result[title] = book
        return result

    def run(self):
        """Scrape!"""
        with open(LINKS_DIR / f"{Category.BOOK.value}.json", "r") as f:
            all_links = json.load(f)

        book_categories = [item.name for item in BookCategory]

        # TODO, make all links a dataclass?
        if set(book_categories) != set(all_links):
            self.logger.warning(f"Book links fields don't match! {set(all_links)}")

        book_archive = BookArchive()
        for category in book_categories:
            links = all_links[category]
            self.logger.info(f"Checking {len(links)} book links from {category}")
            res = {}

            if category == BookCategory.collection.value:
                # links = ["https://genshin-impact.fandom.com/wiki/The_Folio_of_Foliage"]
                res = self._scrape_collection(links)
                book_archive.book_collections = res
            elif category == BookCategory.quest.value:
                # continue
                res = self._scrape_quest(links)
                book_archive.quest_books = res

        output_path = JSON_DIR / f"{Category.BOOK.value}.json"
        self.logger.info(f"Extracted info from {book_archive.count()} links")
        dump_to_json(book_archive.to_dict(), output_path)
