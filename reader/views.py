"""Reader views."""
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import TemplateView

import requests

from reader.tools import parse_article


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

        # Check that url is html
        r = requests.head(article_url)
        if "text/html" not in r.headers["content-type"]:
            return redirect("/help")

        self.article_url = article_url
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self):
        """Return article informations."""
        context = parse_article(self.article_url)
        if context == {}:
            return redirect("/help")
        return context
