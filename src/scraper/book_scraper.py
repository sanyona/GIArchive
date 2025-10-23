import json
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, PageElement

from src.common.type import (BookArchive, BookCategory,
                                       BookCollection, Category, QuestBook,
                                       Volume)
from src.common.archives import JSON_DIR, LINKS_DIR
from src.scraper.base import Scraper
from src.util.file import dump_to_json
from src.util.logger import get_logger
from src.util.url import extract_slug


class BookScraper(Scraper):
    """Scrapes book links from `links/book.json `"""

    def __init__(self):
        self.logger = get_logger("BookScraper")

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

    def _scrape_collection(self, links: list[str]):
        result = {}
        for link in links:
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

                if "version" in h2_text.lower():
                    # get all h3 after this before next h2
                    # iterate through h3
                    h3_list = []

                    # walk siblings after this h2
                    texts = []
                    description = ""
                    first_h3 = True
                    for sib in h2.find_next_siblings():
                        # stop when next <h2> appears
                        if sib.name == "h2":
                            break

                        # collect immediate <h3> section headers
                        if sib.name == "h3":
                            if first_h3:
                                first_h3 = False
                            else:
                                h3_list.append(sib)
                                volume = Volume(
                                    description=description, text="\n".join(texts)
                                )
                                volumes.append(volume)
                                texts = []
                                description = ""

                        if sib.name == "div" and "description-wrapper" in sib.get(
                            "class", []
                        ):
                            desc_el = sib.find("div", class_="description-content")
                            if desc_el:
                                description = desc_el.get_text(strip=True)
                            else:
                                self.logger.warning(
                                    f"no description found for {link} {h2_text}"
                                )

                        if sib.name == "p":
                            texts.append(sib.get_text(separator="\n", strip=True))

                elif "vol" in h2_text.lower():
                    texts = []
                    description = ""
                    for sib in h2.find_next_siblings():
                        if sib.name == "h2":  # stop when it's not <p>/<div>
                            break
                        if sib.name == "div" and "description-wrapper" in sib.get(
                            "class", []
                        ):
                            desc_el = sib.find("div", class_="description-content")
                            if desc_el:
                                description = desc_el.get_text(strip=True)
                            else:
                                self.logger.warning(
                                    f"no description found for {link} {h2_text}"
                                )

                        if sib.name == "p":
                            texts.append(sib.get_text(separator="\n", strip=True))

                    volume = Volume(description=description, text="\n".join(texts))
                    volumes.append(volume)
                else:
                    continue

            book = BookCollection(
                title=title, location=self._scrape_location(soup), volumes=volumes
            )
            result[title] = book
        return result

    def _scrape_quest(self, links: list[str]) -> dict[str, str]:
        """Scraping logic for books under Other Books table (quest books)

        :param links: _description_
        :raises ValueError: _description_
        :return: _description_
        """
        result = {}
        for link in links:
            html = self.get_page(link)
            soup = BeautifulSoup(html, "html.parser")

            title = extract_slug(link)
            # Find the <span> with id="Text"
            text_heading = soup.find("span", id="Text")
            if not text_heading:
                raise ValueError("Text section not found. Page may have changed")

            # 2. Find the parent <h2> to locate the section start
            text_h2 = text_heading.find_parent("h2")

            # 3. Collect everything until the next <h2> (artifact piece)
            texts = []
            for sib in text_h2.find_next_siblings():
                if sib.name == "h2":  # stop when it's not <p>
                    break
                if sib.name == "p":
                    texts.append(sib.get_text(separator="\n", strip=True))

            book = QuestBook(
                title=title, location=self._scrape_location(soup), text="\n".join(texts)
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
            self.logger.warning("Book links fields don't match!")

        book_archive = BookArchive()
        for category in book_categories:
            links = all_links[category]
            self.logger.info(f"Checking {len(links)} book links")
            res = {}
            if category == BookCategory.collection.value:
                res = self._scrape_collection(links)
                book_archive.book_collections = res
            elif category == BookCategory.quest.value:
                res = self._scrape_quest(links)
                book_archive.quest_books = res

        output_path = JSON_DIR / f"{Category.BOOK.value}.json"
        self.logger.info(f"Extracted info from {book_archive.count()} links")
        dump_to_json(book_archive, output_path)
