from abc import ABC
from pathlib import Path

import requests


class Scraper(ABC):

    def get_page(self, url: str) -> str:
        """Use request to get a url's page and returns the HTML

        :param url: _description_
        :return: html as a string
        """
        resp = requests.get(url)
        # TODO, add retry
        resp.raise_for_status()

        return resp.text

    def dump_page_to_file(self, url: str, file: str | Path) -> str:
        """Get a page's html and dump it to a file

        :param url: _description_
        """
        html = self.get_page(url)
        with open(file, "w", encoding="utf-8") as f:
            f.write(html)
        return html

    def load_html_from_file(self, file: str | Path) -> str:
        """Loads html/content from a file

        :param file: _description_
        :return: string
        """
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        return content
