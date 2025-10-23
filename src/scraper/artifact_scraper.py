import json
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, PageElement
from src.common.archives import JSON_DIR, LINKS_DIR
from src.common.book_type import Category
from src.scraper.base import Scraper
from src.util.file import dump_to_json
from src.util.logger import get_logger
from src.util.url import extract_slug


class ArtifactScraper(Scraper):
    """Scrapes artifact lore from links in `links/artifact.json`\n
    Saves scraped artifact lore to `archive/json/artifact.json`

    :param Scraper: _description_
    """

    def __init__(self):
        self.logger = get_logger("ArtifactScraper")

    def run(self):
        """Scrape!

        :raises ValueError: _description_
        """
        with open(LINKS_DIR / f"{Category.ARTIFACT.value}.json", "r") as f:
            links = json.load(f)

        self.logger.info(f"Checking {len(links)} artifact links")
        all_results = {}
        for link in links:
            self.logger.debug(f"Checking {link}")

            page_html = self.get_page(link)
            soup = BeautifulSoup(page_html, "html.parser")

            # get artifact name from the URL
            artifact_name = extract_slug(link)

            # 1. Find the <h2> with id="Lore"
            lore_heading = soup.find("span", id="Lore")
            if not lore_heading:
                raise ValueError("Lore section not found. Page may have changed")

            # 2. Find the parent <h2> to locate the section start
            lore_h2 = lore_heading.find_parent("h2")

            # 4. Parse every element before next h2, get h3 + following text
            # h2: lore heading
            # h3: piece name heading
            # div: description <div class="description-wrapper">
            # div: lore/content
            result = {}
            for elem in lore_h2.find_next_siblings():
                if elem.name == "h2":  # stop at next h2
                    break
                if elem.name != "h3":
                    continue

                # get headline text (h3), artifact name
                title_span = elem.find("span", class_="mw-headline")
                if not title_span:
                    continue
                piece = title_span.get_text(strip=True)

                # get all text immediately after this <h3>, ignoring description-wrapper div
                texts = []
                for sibling in elem.find_next_siblings():
                    # stop at next headline
                    if sibling.name == "h3" or sibling.name == "h2":
                        break

                    # skip description div
                    if sibling.name == "div" and "description-wrapper" in sibling.get(
                        "class", []
                    ):
                        continue

                    if sibling.name == "p":
                        texts.append(sibling.get_text(strip=True))
                    elif sibling.get_text(strip=True):
                        texts.append(sibling.get_text(" ", strip=True))

                result[piece] = "\n".join(texts)

            all_results[artifact_name] = result

        output_path = JSON_DIR / f"{Category.ARTIFACT.value}.json"
        self.logger.info(f"Extracted info from {len(all_results)} links")
        dump_to_json(all_results, output_path)
