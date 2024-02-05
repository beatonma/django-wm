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
            {_link("https://allow-url.org/whatever")}
            {_link("https://deny-url.org/whatever")}
            {_link("ftp://some-ftp-server.com", "FTP server")}
            {_link("smb://some-samba-server.com", "Samba server")}
            Lorem ipsum whatever
        """


class OutgoingLinksTests(OptionsTestCase):
    """Test link discovery in a block of HTML.

    Relative paths and URLs that point to options.domain_name() should only be
    allow if options.allow_self_mentions() is True.

    Links to #id anchors should always be deny.
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
                "https://allow-url.org/whatever",
                "https://deny-url.org/whatever",
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
                "https://allow-url.org/whatever",
                "https://deny-url.org/whatever",
            },
        )

    def test_with_allow_domains(self):
        links = get_target_links_in_html(
            _HTML,
            source_path="/article/1/",
            allow_domains=["allow-url.org"],
        )
        self.assertSetEqual(links, {"https://allow-url.org/whatever"})

    def test_with_deny_domains(self):
        links = get_target_links_in_html(
            _HTML,
            source_path="/article/1/",
            deny_domains=["deny-url.org"],
        )
        self.assertSetEqual(
            links,
            {
                "https://https-absolute-url.org/whatever/",
                "http://http-absolute-url.org/whatever/",
                "https://allow-url.org/whatever",
                config.build_url("/relative-root-path/"),
                config.build_url("/article/1/relative-path/"),
                config.build_url("/something"),
            },
        )

    def test_override_allow(self):
        attr = "wm-deny"

        def _get(html: str):
            return get_target_links_in_html(
                html,
                "",
                allow_domains=["allow.org"],
                deny_domains=None,
                domain_override_attr=attr,
            )

        self.assertSetEqual(
            _get("""<a href="https://allow.org"></a> unrelated-attr"""),
            {"https://allow.org"},
        )
        self.assertSetEqual(_get(f"""<a href="https://allow.org" {attr}></a>"""), set())
        self.assertSetEqual(
            _get(f"""<a href="https://allow.org" data-{attr}></a>"""), set()
        )
        self.assertSetEqual(
            _get(f"""<a href="https://allow.org" class="one {attr} two"></a>"""),
            set(),
        )

    def test_override_deny(self):
        attr = "wm-allow"

        def _get(html: str):
            return get_target_links_in_html(
                html,
                "",
                allow_domains=None,
                deny_domains=["deny.org"],
                domain_override_attr=attr,
            )

        self.assertSetEqual(
            _get("""<a href="https://deny.org" class="unrelated"></a>"""), set()
        )
        self.assertSetEqual(
            _get(f"""<a href="https://deny.org" {attr}></a>"""),
            {"https://deny.org"},
        )
        self.assertSetEqual(
            _get(f"""<a href="https://deny.org" data-{attr}></a>"""),
            {"https://deny.org"},
        )
        self.assertSetEqual(
            _get(f"""<a href="https://deny.org" class="one {attr} two"></a>"""),
            {"https://deny.org"},
        )
