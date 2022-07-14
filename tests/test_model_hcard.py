"""
Ensure HCard objects are correctly built from HTML elements with the 'h-card' class.
"""

import logging
from typing import Optional

from mentions.models import HCard
from mentions.util import html_parser
from tests import WebmentionTestCase

log = logging.getLogger(__name__)


class HCardParsingTests(WebmentionTestCase):
    """MODELS: HCard parsing tests."""

    def _hcard_from_soup(self, html) -> Optional[HCard]:
        soup = html_parser(html)
        return HCard.from_soup(soup)

    def test_with_no_avatar(self):
        """Parse an h-card element with name and homepage but no avatar."""
        hcard = self._hcard_from_soup(
            """<a class="h-card" href="http://joebloggs.com">Joe Bloggs</a>"""
        )

        self.assertEqual(hcard.name, "Joe Bloggs")
        self.assertEqual(hcard.homepage, "http://joebloggs.com")
        self.assertFalse(hcard.avatar)  # Empty str

    def test_with_name_avatar_image(self):
        """Parse an h-card element with all available fields provided."""
        hcard = self._hcard_from_soup(
            """<p class="h-card">
                <img class="u-photo" src="https://janebloggs.org/photo.jpg" alt="" />
                <a class="p-name u-url" href="https://janebloggs.org">Jane Bloggs</a>
                <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
                <span class="p-street-address">17 Austerstræti</span>
                <span class="p-locality">Reykjavík</span>
                <span class="p-country-name">Iceland</span>
            </p>"""
        )

        self.assertEqual(hcard.name, "Jane Bloggs")
        self.assertEqual(hcard.homepage, "https://janebloggs.org")
        self.assertEqual(hcard.avatar, "https://janebloggs.org/photo.jpg")

    def test_with_only_homepage(self):
        """Parse an h-card element with a homepage URL but no name or avatar."""
        hcard = self._hcard_from_soup(
            """<div class="h-card">
                <a class="u-url" href="https://janebloggs.org"></a>
                <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
                <span class="p-street-address">17 Austerstræti</span>
                <span class="p-locality">Reykjavík</span>
                <span class="p-country-name">Iceland</span>
            </div>"""
        )

        self.assertEqual(hcard.homepage, "https://janebloggs.org")
        self.assertFalse(hcard.name)
        self.assertFalse(hcard.avatar)

    def test_hcard_parsing__with_beatonma_hcard(self):
        """Test my own h-card from beatonma.org."""
        hcard = self._hcard_from_soup(
            """
            <div class="h-card vcard u-url">
                    <div class="basic">
                        <img loading="lazy" class="u-photo" src="https://beatonma.org/static/images/avatar.jpg" alt="Photo of Michael Beaton"/>
                        <div class="about">
                            <div class="fn p-name">Michael Beaton</div>
                            <div class="p-addr h-adr">
                                <span class="p-locality">Inverness</span> | <span class="p-region">Scotland</span> | <span class="p-country-name">UK</span>
                            </div>
                        </div>
                    </div>
                    <div data-meta="true">
                        <img loading="lazy" class="u-logo" src="https://beatonma.org/static/images/mb.png" alt="Logo for beatonma.org" width="64"/>
                        <time class="dt-bday" datetime="1987-05-16">1987-05-16</time>
                    </div>
                    <div id="relme">
                        <a rel="me" href="https://beatonma.org" title="Homepage" class="u-url">beatonma.org</a>
                        <!-- etc... -->
                        <a rel="me" href="https://gravatar.com/beatonma" title="Gravatar profile">Gravatar</a>
                    </div>
                </div>"""
        )

        self.assertEqual(hcard.name, "Michael Beaton")
        self.assertEqual(hcard.homepage, "https://beatonma.org")
        self.assertEqual(hcard.avatar, "https://beatonma.org/static/images/avatar.jpg")

    def test_hcard_parsing__with_no_content(self):
        """h-card element with no actual content does not produce an HCard instance."""
        hcard = self._hcard_from_soup("""<a class="h-card"></a>""")

        self.assertIsNone(hcard)

    def test_hcard_parsing__with_no_hcard_element(self):
        """HTML without any h-card element does not produce an HCard object."""
        hcard = self._hcard_from_soup(
            """<div id="some_container"><div class="not-an-h-card"><div class="fake-name">Steve</div></div></div>"""
        )

        self.assertIsNone(hcard)

    def test_hcard_parsing__with_multiple_microformat_items(self):
        hcard = self._hcard_from_soup(
            """<div class="h-entry">
                <div class="h-cite u-in-reply-to">
                    Liked <a class="u-url" href="https://target-url.org">a post</a> by
                    <span class="p-author h-card">
                         <a class="u-url p-name" href="https://example.com">Author Name</a>
                    </span>:
                    <blockquote class="e-content">
                        <p>The post being liked</p>
                    </blockquote>
                </div>
            </div>
            <div class="h-card"><!-- Oops this one has no content --></div>
            <div class="h-card vcard">
                <div class="basic">
                    <img loading="lazy" class="u-photo" src="https://beatonma.org/static/images/avatar.jpg" alt="Photo of Michael Beaton" />
                    <div class="about">
                    <div class="fn p-name">Michael Beaton</div>
                </div>
            </div>
            """
        )

        self.assertEqual(hcard.name, "Michael Beaton")
