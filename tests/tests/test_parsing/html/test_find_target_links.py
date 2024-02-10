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

    def test_with_domains_allow(self):
        links = get_target_links_in_html(
            _HTML,
            source_path="/article/1/",
            domains_allow=["allow-url.org"],
        )
        self.assertSetEqual(links, {"https://allow-url.org/whatever"})

    def test_with_domains_deny(self):
        links = get_target_links_in_html(
            _HTML,
            source_path="/article/1/",
            domains_deny=["deny-url.org"],
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

    def test_with_no_domains_and_tag_override(self):
        send_tag = "wm-send"
        nosend_tag = "wm-nosend"
        html = f"""
        <a href="https://allow.org/by-default/"></a>
        <a href="https://class.org" class="{nosend_tag}"></a>
        <a href="https://data.org" data-{nosend_tag}></a>
        <a href="https://attr.org" {nosend_tag}></a>
        <a href="https://attr.org/unaffected_by_tag" {send_tag}></a>
        """

        self.assertSetEqual(
            get_target_links_in_html(
                html,
                "",
                domains_allow=None,
                domains_deny=None,
                domains_deny_tag=nosend_tag,
            ),
            {"https://allow.org/by-default/", "https://attr.org/unaffected_by_tag"},
        )

    def test_with_domains_allow_and_tag_override(self):
        send_tag = "wm_send"
        nosend_tag = "wm-no-send"
        html = f"""
        <a href="https://allow.org"></a>
        <a href="https://allow.org/unaffected-by-tag/" class={send_tag}></a>
        <a href="https://class.org" class="{nosend_tag}"></a>
        <a href="https://data.org" data-{nosend_tag}></a>
        <a href="https://attr.org" {nosend_tag}></a>
        """

        self.assertSetEqual(
            get_target_links_in_html(
                html,
                "",
                domains_allow={
                    "allow.org",
                    "attr.org",
                    "class.org",
                    "data.org",
                },
                domains_deny=None,
                domains_deny_tag=nosend_tag,
            ),
            {"https://allow.org", "https://allow.org/unaffected-by-tag/"},
        )

    def test_with_domains_deny_and_tag_override(self):
        send_tag = "wm-send"
        nosend_tag = "wm-no_send"
        html = f"""
        <a href="https://deny.org"></a>
        <a href="https://deny.org" {nosend_tag}></a>
        <a href="https://class.org/allow-by-override" class="{send_tag}"></a>
        <a href="https://data.org/allow-by-override" data-{send_tag}></a>
        <a href="https://attr.org/allow-by-override" {send_tag}></a>
        """

        self.assertSetEqual(
            get_target_links_in_html(
                html,
                "",
                domains_allow=None,
                domains_deny={
                    "deny.org",
                    "attr.org",
                    "class.org",
                    "data.org",
                },
                domains_allow_tag=send_tag,
                domains_deny_tag=nosend_tag,
            ),
            {
                "https://class.org/allow-by-override",
                "https://data.org/allow-by-override",
                "https://attr.org/allow-by-override",
            },
        )
