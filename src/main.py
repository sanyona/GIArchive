from src.scraper.artifact_scraper import ArtifactScraper
from src.scraper.link_scraper import LinkScraper


def scrape_artifact():
    artifact_scraper = ArtifactScraper()
    artifact_scraper.run()


def scrape_links():
    scraper = LinkScraper(load_from_file=True)
    scraper.scrape_weapon_links()
    scraper.scrape_artifact_links()
    scraper.scrape_book_links()


if __name__ == "__main__":
    scrape_links()
