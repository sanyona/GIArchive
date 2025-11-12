from src.scraper.artifact_scraper import ArtifactScraper
from src.scraper.book_scraper import BookScraper
from src.scraper.link_scraper import LinkScraper


def scrape_artifact():
    """Scrape artifact from links/artifact.json and saves"""
    artifact_scraper = ArtifactScraper(verbose=True)
    artifact_scraper.run()


def scrape_book():
    """Scrape artifact from links/artifact.json and saves"""
    book_scraper = BookScraper(verbose=True)
    book_scraper.run()


def scrape_links():
    """Scrapes individual page links from main page and save them to links/"""
    scraper = LinkScraper(load_from_file=True)
    scraper.scrape_weapon_links()
    scraper.scrape_artifact_links()
    scraper.scrape_book_links()


if __name__ == "__main__":
    scrape_book()
