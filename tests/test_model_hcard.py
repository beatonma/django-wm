"""
Ensure HCard objects are correctly built from HTML elements with the 'h-card' class.
"""
import logging
from typing import Optional

from mentions.models import HCard
from mentions.tasks.incoming.parsing.hcard import parse_hcard
from mentions.util import html_parser
from tests import WebmentionTestCase

log = logging.getLogger(__name__)


def _hcard_from_soup(html) -> Optional[HCard]:
    soup = html_parser(html)
    return parse_hcard(soup)


class HCardParsingTests(WebmentionTestCase):
    """MODELS: HCard parsing tests."""

    def test_with_all_supported_fields(self):
        """Parse an h-card element with all available fields provided."""
        hcard = _hcard_from_soup(
            """
            <p class="h-card">
                <img class="u-photo" src="https://janebloggs.org/photo.jpg" alt="" />
                <a class="p-name u-url" href="https://janebloggs.org">Jane Bloggs</a>
                <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
                <span class="p-street-address">17 Austerstræti</span>
                <span class="p-locality">Reykjavík</span>
                <span class="p-country-name">Iceland</span>
            </p>
            """
        )

        self.assertEqual(hcard.name, "Jane Bloggs")
        self.assertEqual(hcard.homepage, "https://janebloggs.org")
        self.assertEqual(hcard.avatar, "https://janebloggs.org/photo.jpg")

    def test_with_no_avatar(self):
        """Parse an h-card element with name and homepage but no avatar."""
        hcard = _hcard_from_soup(
            """<a class="h-card" href="http://joebloggs.com">Joe Bloggs</a>"""
        )

        self.assertEqual(hcard.name, "Joe Bloggs")
        self.assertEqual(hcard.homepage, "http://joebloggs.com")
        self.assertFalse(hcard.avatar)  # Empty str

    def test_with_only_homepage(self):
        """Parse an h-card element with a homepage URL but no name."""
        hcard = _hcard_from_soup(
            """
            <div class="h-card">
                <a class="u-url" href="https://janebloggs.org"></a>
                <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
                <span class="p-street-address">17 Austerstræti</span>
                <span class="p-locality">Reykjavík</span>
                <span class="p-country-name">Iceland</span>
            </div>
            """
        )

        self.assertEqual(hcard.homepage, "https://janebloggs.org")
        self.assertFalse(hcard.name)
        self.assertFalse(hcard.avatar)

    def test_with_only_name(self):
        """Parse an h-card element with a name but no homepage."""
        hcard = _hcard_from_soup(
            """
            <div class="h-card">
                <span class="p-name">Jane Bloggs</span>
                <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
                <span class="p-street-address">17 Austerstræti</span>
                <span class="p-locality">Reykjavík</span>
                <span class="p-country-name">Iceland</span>
            </div>
            """
        )

        self.assertEqual(hcard.name, "Jane Bloggs")
        self.assertFalse(hcard.homepage)
        self.assertFalse(hcard.avatar)

    def test_with_beatonma_hcard(self):
        """Test my own h-card from beatonma.org."""
        hcard = _hcard_from_soup(
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
            </div>
            """
        )

        self.assertEqual(hcard.name, "Michael Beaton")
        self.assertEqual(hcard.homepage, "https://beatonma.org")
        self.assertEqual(hcard.avatar, "https://beatonma.org/static/images/avatar.jpg")

    def test_with_missing_content(self):
        """h-card element with no name or homepage does not produce an HCard instance."""
        hcard = _hcard_from_soup(
            """
            <a class="h-card">
                <img loading="lazy" class="u-photo" src="https://beatonma.org/static/images/avatar.jpg"/>
            </a>
            """
        )

        self.assertIsNone(hcard)

    def test_with_no_content(self):
        """h-card element with no actual content does not produce an HCard instance."""
        hcard = _hcard_from_soup("""<a class="h-card"></a>""")

        self.assertIsNone(hcard)

    def test_with_no_hcard_element(self):
        """HTML without any h-card element does not produce an HCard object."""
        hcard = _hcard_from_soup(
            """<div id="some_container"><div class="not-an-h-card"><div class="fake-name">Steve</div></div></div>"""
        )

        self.assertIsNone(hcard)

    def test_with_multiple_microformat_items(self):
        """h-card elements amongst other microformat content are found correctly."""
        hcard = _hcard_from_soup(
            """
            <div class="h-entry">
                <div class="h-cite u-in-reply-to">
                    Liked <a class="u-url" href="https://target-url.org">a post</a> by
                    <span class="p-author h-card">
                         <a class="u-url p-name" href="https://example.com">Commenter Name</a>
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
            </div>
            """
        )

        self.assertEqual(hcard.name, "Michael Beaton")

    def test_prefers_top_level_hcard(self):
        """Retrieves top-level h-card if available."""
        html = """
            <div class="h-entry">
                <div class="h-cite u-in-reply-to">
                    Liked <a class="u-url" href="https://target-url.org">a post</a> by
                    <span class="p-author h-card">
                         <a class="u-url p-name" href="https://example.com">Embedded in h-cite in h-entry</a>
                    </span>:
                    <blockquote class="e-content">
                        <p>The post being liked</p>
                    </blockquote>
                </div>
            </div>
            <div class="h-entry">
                <div class="h-card vcard">
                    <div class="basic">
                        <img loading="lazy" class="u-photo" src="https://beatonma.org/static/images/avatar.jpg" alt="Photo of Michael Beaton" />
                        <div class="about">
                            <div class="fn p-name">Embedded in h-entry</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="arbitrary-non-microformat-nesting">
                <div class="h-card vcard">
                    <div class="basic">
                        <img loading="lazy" class="u-photo" src="https://beatonma.org/static/images/avatar.jpg" alt="Photo of Michael Beaton" />
                        <div class="about">
                            <div class="fn p-name">Top level h-card</div>
                        </div>
                    </div>
                </div>
            </div>
            """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Top level h-card")

    def test_selects_hcard_embedded_in_hentry(self):
        """Retrieves h-card from h-entry author if available."""
        html = """
            <div class="h-entry">
                <div class="h-cite u-in-reply-to">
                    Liked <a class="u-url" href="https://target-url.org">a post</a> by
                    <span class="p-author h-card">
                         <a class="u-url p-name" href="https://example.com">Embedded in h-cite in h-entry</a>
                    </span>:
                    <blockquote class="e-content">
                        <p>The post being liked</p>
                    </blockquote>
                </div>
            </div>
            <article class="h-entry">
                <h1 class="p-name">Microformats are amazing</h1>
                <p>Published by <a class="p-author h-card" href="http://example.com">W. Developer</a>
                   on <time class="dt-published" datetime="2013-06-13 12:00:00">13<sup>th</sup> June 2013</time></p>
              
                <p class="p-summary">In which I extoll the virtues of using microformats.</p>
              
                <div class="e-content">
                    <p>Blah blah blah</p>
                </div>
            </article>
            """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "W. Developer")

    def test_selects_hcard_from_hfeed_author(self):
        """Retrieves h-card from h-feed author if available."""
        html = """
            <div class="h-feed">
                <a class="p-author h-card" href="http://example.com">Feed author</a>
                <article class="h-entry">
                    <h1 class="p-name">Microformats are amazing</h1>
                    <p>Published by <a class="p-author h-card" href="http://example.com">W. Developer</a>
                       on <time class="dt-published" datetime="2013-06-13 12:00:00">13<sup>th</sup> June 2013</time></p>
                  
                    <p class="p-summary">In which I extoll the virtues of using microformats.</p>
                  
                    <div class="e-content">
                        <p>Blah blah blah</p>
                    </div>
                </article>
            </div>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Feed author")

    def test_selects_hcard_embedded_in_hentry_in_hfeed(self):
        """Retrieves h-card from h-entry nested in h-feed."""
        html = """
            <div class="h-feed">
                <div class="h-entry">
                    <div class="h-cite u-in-reply-to">
                        Liked <a class="u-url" href="https://target-url.org">a post</a> by
                        <span class="p-author h-card">
                             <a class="u-url p-name" href="https://example.com">Embedded in h-cite in h-entry</a>
                        </span>:
                        <blockquote class="e-content">
                            <p>The post being liked</p>
                        </blockquote>
                    </div>
                </div>
                <div class="h-entry">
                    <div class="p-author h-card vcard">
                        <div class="basic">
                            <img loading="lazy" class="u-photo" src="https://beatonma.org/static/images/avatar.jpg" alt="Photo of Michael Beaton" />
                            <div class="about">
                                <div class="fn p-name">Embedded in h-entry in h-feed</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Embedded in h-entry in h-feed")
        # raise Exception()

    def test_does_not_select_hcard_in_hcite(self):
        """Ignores h-cards in h-cite (as they belong to someone else)"""
        html = """
            <div class="h-cite u-in-reply-to">
                Liked <a class="u-url" href="https://target-url.org">a post</a> by
                <span class="p-author h-card">
                     <a class="u-url p-name" href="https://example.com">Embedded in h-cite in h-entry</a>
                </span>:
                <blockquote class="e-content">
                    <p>The post being liked</p>
                </blockquote>
            </div>
            """

        hcard = _hcard_from_soup(html)
        self.assertIsNone(hcard)

    def test_avoid_duplcate_hcards(self):
        target = HCard.objects.create(
            homepage="https://beatonma.org",
            name="Michael Beaton",
        )

        name_only = _hcard_from_soup("""<div class="h-card">Michael Beaton</div>""")
        self.assertEqual(target, name_only)

        homepage_only = _hcard_from_soup(
            """<a class="h-card u-url" href="https://beatonma.org"></a>"""
        )
        self.assertEqual(target, homepage_only)

        self.assertEqual(1, HCard.objects.all().count())
