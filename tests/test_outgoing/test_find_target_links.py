from typing import Optional

from mentions import options
from mentions.tasks.outgoing.local import get_target_links_in_html
from tests import OptionsTestCase


def _link(href: str, text: Optional[str] = None):
    return f"""<a href="{href}">{text or ""}</a>"""


class OutgoingLinksTests(OptionsTestCase):
    """Test link discovery in a block of HTML.

    Relative paths and URLs that point to options.domain_name() should only be
    included if options.allow_self_mentions() is True.

    Links to #id anchors should always be excluded.
    """

    def setUp(self) -> None:
        super().setUp()
        self.text = f"""
            Lorem ipsum whatever
            {_link("https://https-absolute-url.org/whatever/", "Absolute https url")}
            Lorem ipsum whatever
            {_link("http://http-absolute-url.org/whatever/", "Absolute http url")}
            {_link("#s3", "Ignore local  # anchor")}
            {_link("/relative-root-path/", "Relative root path self-mention")}
            {_link("relative-path/", "Relative path self-mention")}
            {_link(f"{options.base_url()}/something", "Absolute self-mention")}
            {_link("ftp://some-ftp-server.com", "FTP server")}
            Lorem ipsum whatever
        """

    def test_with_self_mentions_enabled(self):
        self.set_allow_self_mentions(True)

        links = get_target_links_in_html(self.text, source_path="/article/1/")

        self.assertSetEqual(
            links,
            {
                "https://https-absolute-url.org/whatever/",
                "http://http-absolute-url.org/whatever/",
                f"{options.base_url()}/relative-root-path/",
                f"{options.base_url()}/article/1/relative-path/",
                f"{options.base_url()}/something",
            },
        )

    def test_with_self_mentions_disabled(self):
        self.set_allow_self_mentions(False)

        links = get_target_links_in_html(self.text, source_path="/article/1/")

        self.assertSetEqual(
            links,
            {
                "https://https-absolute-url.org/whatever/",
                "http://http-absolute-url.org/whatever/",
            },
        )

    def test_relative_paths(self):
        base_url = options.base_url()

        relpath = _link("whatever")
        self.assertSetEqual(
            {f"{base_url}/article/1/whatever"},
            get_target_links_in_html(relpath, source_path="/article/1/"),
        )

        self.assertSetEqual(
            {f"{base_url}/article/whatever"},
            get_target_links_in_html(relpath, source_path="/article/1"),
        )

        rootpath = _link("/whatever")
        self.assertSetEqual(
            {f"{base_url}/whatever"},
            get_target_links_in_html(rootpath, source_path="/article/1/"),
        )

        self.assertSetEqual(
            {f"{base_url}/whatever"},
            get_target_links_in_html(rootpath, source_path="/article/1"),
        )
