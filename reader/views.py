"""Reader views."""
from urllib.parse import urlparse

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import TemplateView

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


class HelpView(TemplateView):
    """Help view."""

    template_name = "reader/help.html"


class ReaderView(TemplateView):
    """ReaderView."""

    template_name = "reader/clean.html"

    def dispatch(self, request, *args, **kwargs):
        """Validate article url."""
        article_url = request.GET.get("u")
        if not article_url:
            return redirect("/help")

        if not article_url.startswith("http"):
            article_url = f"http://{article_url}"

        try:
            URLValidator()(article_url)
        except ValidationError:
            return redirect("/help")

        self.article_url = article_url
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self):
        """Return article informations."""
        source = requests.get(self.article_url)
        urlparsed = urlparse(self.article_url)
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

        return {
            "title": doc.short_title(),
            "content": str(soup),
            "url": self.article_url,
        }
