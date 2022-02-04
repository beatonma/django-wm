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
            """<p class="h-card"><img class="u-photo" src="https://janebloggs.org/photo.jpg" alt="" /><a class="p-name u-url" href="https://janebloggs.org">Jane Bloggs</a><a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,<span class="p-street-address">17 Austerstræti</span><span class="p-locality">Reykjavík</span><span class="p-country-name">Iceland</span></p>"""
        )

        self.assertEqual(hcard.name, "Jane Bloggs")
        self.assertEqual(hcard.homepage, "https://janebloggs.org")
        self.assertEqual(hcard.avatar, "https://janebloggs.org/photo.jpg")

    def test_with_only_homepage(self):
        """Parse an h-card element with a homepage URL but no name or avatar."""
        hcard = self._hcard_from_soup(
            """<div class="h-card"><a class="u-url" href="https://janebloggs.org"></a><a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,<span class="p-street-address">17 Austerstræti</span><span class="p-locality">Reykjavík</span><span class="p-country-name">Iceland</span></div>"""
        )

        self.assertEqual(hcard.homepage, "https://janebloggs.org")
        self.assertFalse(hcard.name)
        self.assertFalse(hcard.avatar)

    def test_hcard_parsing__with_beatonma_hcard(self):
        """Test my own h-card from beatonma.org."""
        hcard = self._hcard_from_soup(
            """<div id="some_container"><div class="h-card flex-row-center footer"><a rel="me" href="https://beatonma.org" class="u-url foot-link" alt="beatonma.org" aria-label="beatonma.org"><div class="tooltip"><svg id="footer_icon_home" class="foot-icon" viewBox="0 0 48 48"><path d="M 19.6,42.8 L 19.6,29.5 L 28.5,29.5 L 28.5,42.8 L 39.6,42.8 L 39.6,25 L 46.3,25 L 24,5.05 L 1.75,25 L 8.45,25 L 8.45,42.8 Z"/></svg><div class="tooltip-popup">beatonma.org</div></div></a><a rel="me" href="https://play.google.com/store/apps/developer?id=Michael+Beaton" class="foot-link" alt="Play Store" aria-label="Play Store"><div class="tooltip"><svg id="footer_icon_playstore" class="foot-icon" viewBox="0 0 48 48"><path d="M 32.5,30.6 L 6.66,4.71 M 32.5,17.4 L 6.72,43.3 M 32.5,30.6 C 45,23.2 44.5,24.4 32.5,17.4 L 9.92,4.76 C 9.02,4.19 7.39,3.53 6.66,4.71 C 6.48,5.01 6.35,5.42 6.31,5.99 L 6.34,42 C 6.34,42.6 6.48,43 6.72,43.3 C 7.41,44.2 8.92,44 10.1,43.4 Z"/></svg><div class="tooltip-popup">Play Store</div></div></a><a rel="me" href="https://github.com/beatonma" class="foot-link" alt="Github" aria-label="Github"><div class="tooltip"><svg id="footer_icon_github" class="foot-icon" viewBox="0 0 48 48"><path d="M 24 3.95 C 12.7 3.95 3.45 13.1 3.45 24.6 C 3.45 33.6 9.35 41.2 17.5 43.9 C 18.6 44.1 18.9 43.5 18.9 43 C 18.9 42.5 18.9 41.2 18.9 39.5 C 13.2 40.7 12 36.7 12 36.7 C 11 34.3 9.65 33.7 9.65 33.7 C 7.85 32.5 9.89 32.5 9.89 32.5 C 11.9 32.7 13 34.6 13 34.6 C 14.8 37.7 17.8 36.8 19 36.3 C 19.1 34.9 19.7 34 20.3 33.6 C 15.7 33.1 10.9 31.4 10.9 23.4 C 10.9 21.3 11.7 19.4 13 18 C 12.8 17.5 12.1 15.4 13.2 12.5 C 13.2 12.5 15 11.9 18.9 14.6 C 20.5 14.1 22.3 13.8 24 13.8 C 25.8 13.8 27.5 14.1 29.2 14.6 C 33 11.9 34.8 12.5 34.8 12.5 C 36 15.4 35.2 17.5 35 18 C 36.3 19.4 37.1 21.3 37.1 23.4 C 37.1 31.4 32.3 33.1 27.7 33.6 C 28.5 34.2 29.1 35.4 29.1 37.3 C 29.1 40.1 29.1 42.3 29.1 43 C 29.1 43.5 29.5 44.1 30.6 43.9 C 38.6 41.2 44.5 33.6 44.5 24.6 C 44.5 13.1 35.3 3.95 24 3.95"/></svg><div class="tooltip-popup">Github</div></div></a><a rel="me" href="https://twitter.com/_beatonma" class="foot-link" alt="Twitter" aria-label="Twitter"><div class="tooltip"><svg id="footer_icon_twitter" class="foot-icon" viewBox="0 0 56 48"><path d="M 18.7 44 C 37.2 44 47.7 29 47.7 15 C 47.7 15 47.7 14 47.7 14 C 49.7 13 51.7 11 52.7 8.95 C 50.7 9.95 48.7 9.95 46.7 9.95 C 48.7 8.95 50.7 6.95 51.7 4.95 C 49.7 5.95 46.7 6.95 44.7 6.95 C 42.7 4.95 40.2 3.95 37.4 3.95 C 31.7 3.95 27.2 8.95 27.2 14 C 27.2 15 27.4 16 27.6 16 C 19.1 16 11.6 12 6.7 5.95 C 5.8 6.95 5.3 8.95 5.3 11 C 5.3 14 7.1 18 9.8 19 C 8.2 19 6.6 19 5.3 18 C 5.3 18 5.3 18 5.3 18 C 5.3 23 8.8 27 13.4 28 C 12.4 28 11.6 28 10.7 28 C 10.1 28 9.4 28 8.8 28 C 10.1 32 13.8 35 18.3 35 C 14.8 38 10.4 40 5.7 40 C 4.9 40 4.1 40 3.3 39 C 7.7 42 13 44 18.7 44"/></svg><div class="tooltip-popup">Twitter</div></div></a><a rel="me" href="/feed" class="foot-link noanim" alt="RSS feed" aria-label="RSS feed"><div class="tooltip"><svg id="footer_icon_feed" class="foot-icon" viewBox="0 0 48 48"><circle cx="9.6" cy="38.3" r="5.59"/><path d="M 4 3.95 L 4 11.4 C 21.9 11.4 36.6 26.1 36.6 44 L 44 44 C 44 21.9 26.1 3.95 4 3.95 Z M 4 18.6 L 4 25.8 C 14 25.8 22.2 34 22.2 44 L 29.4 44 C 29.4 29.9 18.1 18.6 4 18.6 Z"/></svg><div class="tooltip-popup">RSS feed</div></div></a><div class="nodisplay"><span class="p-name">Michael Beaton</span><span class="p-region">Scotland</span><span class="p-country-name">UK</span><div class="dt-bday">1987-05-16</div><img class="u-logo u-photo" src="https://beatonma.org/static/images/mb.png" /><a rel="me" href="https://www.last.fm/user/schadenfreude87" aria-label="Last.fm profile page">My listening habits since 2005</a><a rel="me" href="https://userstyles.org/users/365999" aria-label="Userstyles.org profile page">Custom CSS style overrides</a><a rel="me" href="http://eu.battle.net/sc2/en/profile/2784180/1/fallofmath/" aria-label="StarCraft II battle.net profile page">StarCraft II</a><a rel="me" href="https://www.duolingo.com/fallofmath" aria-label="Duolingo profile page">Duolingo</a><a rel="me" href="https://gravatar.com/beatonma" aria-label="Gravatar profile page">Gravatar</a><a rel="webmention" href="https://beatonma.org/webmention/" aria-label="Webmention endpoint for beatonma.org" /></div></div></div>"""
        )

        self.assertEqual(hcard.name, "Michael Beaton")
        self.assertEqual(hcard.homepage, "https://beatonma.org")
        self.assertEqual(hcard.avatar, "https://beatonma.org/static/images/mb.png")

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
