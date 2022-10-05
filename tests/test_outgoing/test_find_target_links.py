from mentions import options
from mentions.tasks.outgoing.local import get_target_links_in_html
from tests import OptionsTestCase


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
            <a href="https://https-absolute-url.org/whatever/">Absolute https url</a>
            Lorem ipsum whatever
            <a href="http://http-absolute-url.org/whatever/">Absolute http url</a>
            <a href="#s3">Ignore local #anchor</a>
            <a href="/relative-root-path/">Relative root path self-mention</a>
            <a href="relative-path/">Relative path self-mention</a>
            <a href="https://{options.domain_name()}/something">Absolute self-mention</a>
            <a href="ftp://some-ftp-server.com">FTP server</a>
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
                f"https://{options.domain_name()}/relative-root-path/",
                f"https://{options.domain_name()}/article/1/relative-path/",
                f"https://{options.domain_name()}/something",
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
