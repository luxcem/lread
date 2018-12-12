"""Reader tools."""

from urllib.parse import urlparse
import bleach
import requests
from bs4 import BeautifulSoup
from readability import Document


ALLOWED_TAGS = [
    "a",
    "b",
    "blockquote",
    "br",
    "br",
    "code",
    "dd",
    "del",
    "dl",
    "dt",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "kbd",
    "li",
    "ol",
    "p",
    "pre",
    "q",
    "s",
    "span",
    "strike",
    "strong",
    "sub",
    "sup",
    "ul",
]

ALLOWED_ATTRS = {"a": ("href", "rel"), "img": ("alt", "src")}


def parse_article(article_url):
    """Parse an online article."""
    source = requests.get(article_url, verify=True, timeout=2)
    urlparsed = urlparse(article_url)
    hostname = "{scheme}://{netloc}".format(
        scheme=urlparsed.scheme, netloc=urlparsed.netloc
    )
    doc = Document(source.text)

    content = bleach.clean(
        doc.summary(), tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True
    )
    soup = BeautifulSoup(content)

    for img in soup.findAll("img"):
        if img["src"].startswith("http"):
            continue
        img["src"] = "{root}/{src}".format(root=hostname, src=img["src"])

    for link in soup.findAll("link"):
        if link["href"].startswith("http"):
            continue
        link["href"] = "{root}/{src}".format(root=hostname, src=img["href"])

    return {"title": doc.short_title(), "content": str(soup), "url": article_url}
