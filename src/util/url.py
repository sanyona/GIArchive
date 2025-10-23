from urllib.parse import unquote, urlparse


def extract_slug(link: str) -> str:
    """Extracts the last segment / slug of a url\n
    Example: https://genshin-impact.fandom.com/wiki/Dreams_of_the_Ancient_Capital\n
    Returns: Dreams of the Ancient Capital

    :param link: url, e.g.
    :return: _description_
    """
    last_part = urlparse(link).path.split("/")[-1]
    decoded = unquote(last_part)
    slug = decoded.replace("_", " ")
    return slug
