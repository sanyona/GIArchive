"""Scrapes artifact from links/artifact.json"""

import json

from bs4 import BeautifulSoup

from src.common.archives import JSON_DIR, LINKS_DIR
from src.common.type import Artifact, ArtifactSet, Category
from src.scraper.base import Scraper
from src.util.file import dump_to_json
from src.util.logger import get_logger
from src.util.txt import clean_text
from src.util.url import extract_slug


class ArtifactScraper(Scraper):
    """Scrapes artifact lore from links in `links/artifact.json`\n
    Saves scraped artifact lore to `archive/json/artifact.json`

    :param Scraper: _description_
    """

    def __init__(self, verbose=False):
        self.logger = get_logger("ArtifactScraper", verbose=verbose)

    def run(self):
        """Scrape!

        :raises ValueError: _description_
        """
        with open(LINKS_DIR / f"{Category.ARTIFACT.value}.json", "r") as f:
            links = json.load(f)

        self.logger.info(f"Checking {len(links)} artifact links")
        all_results: dict[str, ArtifactSet] = {}
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
            # h3: <span> piece name heading
            # div: <div> description <div class="description-wrapper">
            # div: <p> lore/content
            artifacts = []

            piece_name, description, text = "", "", ""
            for elem in lore_h2.find_next_siblings():

                if elem.name == "h2":  # stop at next h2
                    break

                if elem.name == "h3":
                    # get headline text (h3), artifact name
                    title_span = elem.find("span", class_="mw-headline")
                    if not title_span:
                        continue
                    piece_name = title_span.get_text(strip=True)

                    self.logger.debug(piece_name)

                    # collect all <div> siblings until the next <h3>
                    # usually just 2, but some artifact has no text (1 div)
                    next_divs = []
                    for sibling in elem.find_next_siblings():
                        if sibling.name in ["h3", "h2"]:  # stop at next header
                            break
                        if sibling.name == "div":
                            next_divs.append(sibling)

                    desc_div = next_divs[0]
                    desc_el = desc_div.find("div", class_="description-content")
                    # TODO error ahdnling
                    description = desc_el.get_text(strip=True)

                    if len(next_divs) > 1:
                        text_div = next_divs[1]
                        text = text_div.get_text(separator=" ", strip=True)

                    artifact = Artifact(
                        name=piece_name, description=description, text=clean_text(text)
                    )
                    artifacts.append(artifact)

            all_results[artifact_name] = ArtifactSet(
                name=artifact_name, artifacts=artifacts
            )
            self.logger.debug(all_results[artifact_name])

        output_path = JSON_DIR / f"{Category.ARTIFACT.value}.json"
        self.logger.info(f"Extracted info from {len(all_results)} links")

        dump_to_json({k: v.to_dict() for k, v in all_results.items()}, output_path)
