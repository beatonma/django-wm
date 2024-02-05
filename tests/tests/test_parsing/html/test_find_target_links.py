from typing import Optional

from mentions import config
from mentions.tasks.outgoing.local import get_target_links_in_html
from tests.tests.util.testcase import OptionsTestCase


def _link(href: str, text: Optional[str] = None):
    return f"""<a href="{href}">{text or ""}</a>"""


_HTML = f"""
            Lorem ipsum whatever
            {_link("https://https-absolute-url.org/whatever/", "Absolute https url")}
            Lorem ipsum whatever
            {_link("http://http-absolute-url.org/whatever/", "Absolute http url")}
            {_link("#s3", "Ignore local #anchor")}
            {_link("/relative-root-path/", "Relative root path self-mention")}
            {_link("relative-path/", "Relative path self-mention")}
            {_link(config.build_url("/something"), "Absolute self-mention")}
            {_link("https://included-url.org/whatever")}
            {_link("https://excluded-url.org/whatever")}
            {_link("ftp://some-ftp-server.com", "FTP server")}
            {_link("smb://some-samba-server.com", "Samba server")}
            Lorem ipsum whatever
        """


class OutgoingLinksTests(OptionsTestCase):
    """Test link discovery in a block of HTML.

    Relative paths and URLs that point to options.domain_name() should only be
    included if options.allow_self_mentions() is True.

    Links to #id anchors should always be excluded.
    """

    def test_relative_paths(self):
        relpath = _link("whatever")
        self.assertSetEqual(
            {config.build_url("/article/1/whatever")},
            get_target_links_in_html(relpath, source_path="/article/1/"),
        )

        self.assertSetEqual(
            {config.build_url("/article/whatever")},
            get_target_links_in_html(relpath, source_path="/article/1"),
        )

        rootpath = _link("/whatever")
        self.assertSetEqual(
            {config.build_url("/whatever")},
            get_target_links_in_html(rootpath, source_path="/article/1/"),
        )

        self.assertSetEqual(
            {config.build_url("/whatever")},
            get_target_links_in_html(rootpath, source_path="/article/1"),
        )

    def test_with_self_mentions_enabled(self):
        links = get_target_links_in_html(
            _HTML,
            source_path="/article/1/",
            allow_self_mentions=True,
        )

        self.assertSetEqual(
            links,
            {
                "https://https-absolute-url.org/whatever/",
                "http://http-absolute-url.org/whatever/",
                "https://included-url.org/whatever",
                "https://excluded-url.org/whatever",
                config.build_url("/relative-root-path/"),
                config.build_url("/article/1/relative-path/"),
                config.build_url("/something"),
            },
        )

    def test_with_self_mentions_disabled(self):
        links = get_target_links_in_html(
            _HTML,
            source_path="/article/1/",
            allow_self_mentions=False,
        )

        self.assertSetEqual(
            links,
            {
                "https://https-absolute-url.org/whatever/",
                "http://http-absolute-url.org/whatever/",
                "https://included-url.org/whatever",
                "https://excluded-url.org/whatever",
            },
        )

    def test_with_included_domains(self):
        links = get_target_links_in_html(
            _HTML,
            source_path="/article/1/",
            included_domains=["included-url.org"],
        )
        self.assertSetEqual(links, {"https://included-url.org/whatever"})

    def test_with_excluded_domains(self):
        links = get_target_links_in_html(
            _HTML,
            source_path="/article/1/",
            excluded_domains=["excluded-url.org"],
        )
        self.assertSetEqual(
            links,
            {
                "https://https-absolute-url.org/whatever/",
                "http://http-absolute-url.org/whatever/",
                "https://included-url.org/whatever",
                config.build_url("/relative-root-path/"),
                config.build_url("/article/1/relative-path/"),
                config.build_url("/something"),
            },
        )
