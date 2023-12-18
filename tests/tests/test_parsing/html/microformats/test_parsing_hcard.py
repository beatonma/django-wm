"""
Ensure HCard objects are correctly built from HTML elements with the 'h-card' class.
"""
import logging
from typing import Callable, Optional, Union

from mentions.models import HCard
from mentions.tasks.incoming.remote import get_metadata_from_source
from tests.tests.util import testfunc
from tests.tests.util.testcase import WebmentionTestCase

log = logging.getLogger(__name__)

MENTIONED_URL = testfunc.random_url()
MENTION_ANCHOR = f"""<a href="{MENTIONED_URL}">Our content</a>"""


def _hcard_from_soup(
    html: str,
    source_url: Union[Callable, str] = testfunc.random_url,
) -> Optional[HCard]:
    if callable(source_url):
        source_url = source_url()
    return get_metadata_from_source(
        html,
        target_url=MENTIONED_URL,
        source_url=source_url,
    ).hcard


class TopLevelHCardParsingTests(WebmentionTestCase):
    """PARSING: Parse h-card at top-level."""

    def test_with_all_supported_fields(self):
        """Parse an h-card element with all available fields provided."""

        html = f"""
            <body>
            <article>
                Blah blah blah {MENTION_ANCHOR} how interesting.
            </article>

            <p class="h-card">
                <img class="u-photo" src="https://janebloggs.org/photo.jpg" alt="" />
                <a class="p-name u-url" href="https://janebloggs.org">Jane Bloggs</a>
                <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
                <span class="p-street-address">17 Austerstræti</span>
                <span class="p-locality">Reykjavík</span>
                <span class="p-country-name">Iceland</span>
            </p>
            </body>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Jane Bloggs")
        self.assertEqual(hcard.homepage, "https://janebloggs.org")
        self.assertEqual(hcard.avatar, "https://janebloggs.org/photo.jpg")

    def test_with_no_avatar(self):
        """Parse an h-card element with name and homepage but no avatar."""

        html = f"""
            Blah blah blah {MENTION_ANCHOR}
            <a class="h-card" href="http://joebloggs.com">Joe Bloggs</a>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Joe Bloggs")
        self.assertEqual(hcard.homepage, "http://joebloggs.com")
        self.assertFalse(hcard.avatar)  # Empty str

    def test_with_logo_avatar(self):
        html = f"""
            Blah blah blah {MENTION_ANCHOR}
            <div class="h-card">
                <span class="p-name">Jane Bloggs</span>
                <img loading="lazy" class="u-logo" src="https://beatonma.org/static/images/logo.png"/>
            </div>
        """
        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.avatar, "https://beatonma.org/static/images/logo.png")

    def test_photo_preferred_over_logo(self):
        html = f"""
            Blah blah blah {MENTION_ANCHOR}
            <div class="h-card">
                <span class="p-name">Jane Bloggs</span>
                <img loading="lazy" class="u-photo" src="https://beatonma.org/static/images/photo.png"/>
                <img loading="lazy" class="u-logo" src="https://beatonma.org/static/images/logo.png"/>
            </div>
        """
        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.avatar, "https://beatonma.org/static/images/photo.png")

    def test_with_only_homepage(self):
        """Parse an h-card element with a homepage URL but no name."""

        html = f"""
            Blah blah blah {MENTION_ANCHOR}
            <div class="h-card">
                <a class="u-url" href="https://janebloggs.org"></a>
                <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
                <span class="p-street-address">17 Austerstræti</span>
                <span class="p-locality">Reykjavík</span>
                <span class="p-country-name">Iceland</span>
            </div>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.homepage, "https://janebloggs.org")
        self.assertFalse(hcard.name)
        self.assertFalse(hcard.avatar)

    def test_with_only_name(self):
        """Parse an h-card element with a name but no homepage."""

        html = f"""
            Blah blah blah {MENTION_ANCHOR}
            <div class="h-card">
                <span class="p-name">Jane Bloggs</span>
                <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
                <span class="p-street-address">17 Austerstræti</span>
                <span class="p-locality">Reykjavík</span>
                <span class="p-country-name">Iceland</span>
            </div>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Jane Bloggs")
        self.assertFalse(hcard.homepage)
        self.assertFalse(hcard.avatar)

    def test_with_missing_content(self):
        """h-card element with no name or homepage does not produce an HCard instance."""

        html = f"""
            Blah blah blah {MENTION_ANCHOR}
            <a class="h-card">
                <img loading="lazy" class="u-photo" src="https://beatonma.org/static/images/avatar.jpg"/>
            </a>
        """

        hcard = _hcard_from_soup(html)
        self.assertIsNone(hcard)

    def test_with_no_content(self):
        """h-card element with no actual content does not produce an HCard instance."""

        html = f"""
            Blah blah blah {MENTION_ANCHOR}
            <a class="h-card"></a>
        """

        hcard = _hcard_from_soup(html)
        self.assertIsNone(hcard)

    def test_with_no_hcard_element(self):
        """HTML without any h-card element does not produce an HCard object."""

        html = f"""
            Blah blah blah {MENTION_ANCHOR}
            <div id="some_container">
                <div class="not-an-h-card">
                    <div class="p-name">Steve</div>
                </div>
            </div>
        """

        hcard = _hcard_from_soup(html)
        self.assertIsNone(hcard)

    def test_with_beatonma_hcard(self):
        """Test my own h-card from beatonma.org."""

        html = f"""
            Blah blah blah {MENTION_ANCHOR}
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

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Michael Beaton")
        self.assertEqual(hcard.homepage, "https://beatonma.org")
        self.assertEqual(hcard.avatar, "https://beatonma.org/static/images/avatar.jpg")

    def test_with_multiple_microformat_items(self):
        """h-card elements amongst other microformat content are found correctly."""

        html = f"""
            Blah blah blah {MENTION_ANCHOR}
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

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Michael Beaton")

    def test_top_level_hcard_when_none_in_hentry(self):
        """Falls back to top-level h-card when not available in h-entry"""

        html = f"""
        <div class="h-card">Michael Beaton</div>
        
        <div class="h-entry">
            This entry mentions our link {MENTION_ANCHOR} but does not include
            its own h-card.
        </div>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Michael Beaton")


class EmbeddedHCardParsingTests(WebmentionTestCase):
    """PARSING: Parse h-card embedded in microformat containers (h-entry, h-feed)."""

    def test_selects_hcard_from_hentry_author(self):
        """Retrieves h-card from h-entry author if available."""

        html = f"""
            <div class="h-entry">
                <div class="h-cite u-in-reply-to">
                    Liked <a class="u-url" href="https://some-url.com">a post</a> by
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
                <p>Published by <a class="p-author h-card" href="http://example.com">Correct name</a>
                   on <time class="dt-published" datetime="2013-06-13 12:00:00">13<sup>th</sup> June 2013</time></p>

                <p class="p-summary">In which I extol the virtues of using microformats.</p>

                <div class="e-content">
                    <p><a href="{MENTIONED_URL}">Links to our content</a></p>
                </div>
            </article>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Correct name")

    def test_selects_hcard_from_hfeed_author(self):
        """Retrieves h-card from h-feed author if available."""

        html = f"""
            <div class="h-feed">
                <a class="p-author h-card" href="http://example.com">Feed author</a>
                <article class="h-entry">
                    <h1 class="p-name">Microformats are amazing</h1>

                    <p class="p-summary">In which I extol the virtues of using microformats.</p>

                    <div class="e-content">
                        <p><a href="{MENTIONED_URL}">Links to our content</a></p>
                    </div>
                </article>
            </div>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Feed author")

    def test_does_not_select_hcard_in_hcite(self):
        """Ignores h-cards in h-cite (as they belong to someone else)"""

        html = f"""
            <div class="h-cite u-in-reply-to">
                Liked <a class="u-url" href="{MENTIONED_URL}">a post</a> by
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

    def test_selects_associated_hcard(self):
        """Selects the h-card associated with the webmention link, not an unrelated one."""

        html = f"""
        <div class="h-feed">
            <article class="h-entry">
                <h1 class="p-name">Microformats are amazing</h1>
                <p>Published by <a class="p-author h-card" href="http://example.com">Unrelated author</a>
                   on <time class="dt-published" datetime="2013-06-13 12:00:00">13<sup>th</sup> June 2013</time></p>

                <p class="p-summary">In which I extol the virtues of using microformats.</p>

                <div class="e-content">
                    <p>This post does NOT link to our content.</p>
                </div>
            </article>
            <article class="h-entry">
                <h1 class="p-name">Microformats are amazing</h1>
                <p>Published by <a class="p-author h-card" href="http://example.com">Relevant author</a>
                   on <time class="dt-published" datetime="2013-06-13 12:00:00">13<sup>th</sup> June 2013</time></p>

                <p class="p-summary">In which I extol the virtues of using microformats.</p>

                <div class="e-content">
                    <p>This post <a href="{MENTIONED_URL}">links to our content</a></p>
                </div>
            </article>
        </div>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Relevant author")

    def test_top_level_hcard_when_none_in_hentry(self):
        """Prefers most closely-related h-card."""
        html = f"""
        <div class="h-card">Top level</div>

        <div class="h-entry">
            <div class="h-card">Embedded in post</div>
            
            This entry mentions our link {MENTION_ANCHOR} but does not include
            its own h-card.
        </div>
        """

        hcard = _hcard_from_soup(html)
        self.assertEqual(hcard.name, "Embedded in post")

    def test_relative_urls_are_converted(self):
        source_url = "https://my-hcard.org/"
        html = f"""
        Blah blah blah {MENTION_ANCHOR}
        <p class="h-card">
            <img class="u-photo" src="/photo.jpg" alt="" />
            <a class="p-name u-url" href="/">Jane Bloggs</a>
            <a class="u-email" href="mailto:janebloggs@janebloggs.com">janebloggs@janebloggs.com</a>,
            <span class="p-street-address">17 Austerstræti</span>
            <span class="p-locality">Reykjavík</span>
            <span class="p-country-name">Iceland</span>
        </p>
        """

        hcard = _hcard_from_soup(html, source_url=source_url)
        self.assertEqual(hcard.avatar, "https://my-hcard.org/photo.jpg")
        self.assertEqual(hcard.homepage, "https://my-hcard.org/")
