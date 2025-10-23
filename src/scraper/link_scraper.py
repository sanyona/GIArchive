import json
import urllib.parse
import pathlib
from bs4 import BeautifulSoup, Tag
from src.common.type import BookCategory, Category
from src.common.archives import HTML_DIR, LINKS_DIR
from src.scraper.base import Scraper
from src.util.logger import get_logger
from src.common.links import BASE_LINK, BOOK_COL_ID, OTHER_BOOK_ID, links2html_mapping

CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
PARENT_DIR = pathlib.Path(__file__).parent.parent.resolve()


class LinkScraper(Scraper):
    """Scrapes item link from the main links in links.py for artifact, book, and weapons\n
    Saves the HTML if sent a page request, else loads from archive files\n
    Saves scraped item links to `links/`
    """

    def __init__(self, load_from_file: bool = True) -> None:
        self.load_from_file = load_from_file
        self.logger = get_logger()

        self.name2html: dict[str, str] = {}
        # load from url and save to file
        if not self.load_from_file:
            for name, link in links2html_mapping.items():
                html = self.dump_page_to_file(link, HTML_DIR / f"{name}.html")
                self.name2html[name] = html
        else:  # TODO, check if file exists/empty, if it is, go visit page
            for name in links2html_mapping:
                html = self.load_html_from_file(HTML_DIR / f"{name}.html")
                self.name2html[name] = html

    def select_nth_cells_from_table(self, table: Tag, index: int) -> list[str]:
        """Extract links from nth cell given a table

        :param table: _description_
        :param cell: _description_
        :return: _description_
        """
        links = []
        rows = table.select("tr")[1:]
        for row in rows:
            cells = row.select("td")
            link = cells[index].find("a")["href"]
            links.append(urllib.parse.urljoin(BASE_LINK, link))
        return links

    def scrape_artifact_links(self) -> list[str]:
        """Parse artifact set link HTML and extract individual links

        :param html: _description_
        """
        self.logger.info("Scraping artifact links")
        html = self.name2html[Category.ARTIFACT.value]
        soup = BeautifulSoup(html, "html.parser")

        # Findthe table with css selector "wikitable"
        tables = soup.select(".wikitable")

        # expect one table
        if len(tables) != 1:
            self.logger.warning("The page may have changed.")

        links = []
        table = tables[0]
        links = self.select_nth_cells_from_table(table=table, index=0)

        self.logger.info(f"{len(links)} artifact links scraped.")

        with open(LINKS_DIR / f"{Category.ARTIFACT.value}.json", "w") as f:
            json.dump(links, f, indent=4, sort_keys=True)

        return links

    def scrape_weapon_links(self) -> list[str]:
        """Scrape individual weapon links from html

        :return: a list of links
        """
        self.logger.info("Scraping weapon links")
        html = self.name2html[Category.WEAPON.value]

        soup = BeautifulSoup(html, "html.parser")
        tables = soup.select(".article-table")

        # expect at least one table
        if len(tables) < 1:
            self.logger.warning("The page may have changed.")

        links = []
        table = tables[0]
        # TODO  verify with heading?
        links = self.select_nth_cells_from_table(table=table, index=1)

        self.logger.info(f"{len(links)} weapon links scraped.")

        with open(LINKS_DIR / f"{Category.WEAPON.value}.json", "w") as f:
            json.dump(links, f, indent=4, sort_keys=True)

        return links

    def scrape_book_links(self) -> list[str]:
        """Scrape individual weapon links from html

        :return: a list of links
        """
        self.logger.info("Scraping book links")
        html = self.name2html[Category.BOOK.value]

        soup = BeautifulSoup(html, "html.parser")

        # There are two tables. List of books + Other books
        tables = soup.select(".article-table")

        # expect 2 tables
        if len(tables) <= 2:
            self.logger.warning("The page may have changed.")

        links = {}

        # first table
        main_table = tables[0]

        # TODO make it a constant

        heading = main_table.find_previous("span", id=BOOK_COL_ID)
        header_text = heading.get_text(strip=True).lower()
        assert header_text == "List of Book Collections".lower()

        # TODO enum or soemthing
        links[BookCategory.collection.value] = self.select_nth_cells_from_table(
            table=main_table, index=1
        )

        self.logger.info(
            f"{len(links[BookCategory.quest.value])} main book links scraped."
        )

        # 2nd table
        quest_table = tables[1]

        heading = quest_table.find_previous("span", id=OTHER_BOOK_ID)
        header_text = heading.get_text(strip=True).lower()
        assert (
            header_text == "Other Books".lower()
        ), f"{header_text} didn't match other books"

        links[BookCategory.quest.value] = self.select_nth_cells_from_table(
            table=quest_table, index=1
        )

        self.logger.info(
            f"{len(links[BookCategory.quest.value])} quest book links scraped."
        )

        with open(LINKS_DIR / f"{Category.BOOK.value}.json", "w") as f:
            json.dump(links, f, indent=4, sort_keys=True)

        return links
