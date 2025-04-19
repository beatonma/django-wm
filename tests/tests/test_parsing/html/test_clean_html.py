from mentions.util import html_parser
from tests.tests.util.testcase import WebmentionTestCase


def _html(content: str) -> str:
    return f"""<html><head></head><body>{content}</body></html>"""


class HtmlCleanTests(WebmentionTestCase):
    def test_html_clean(self):
        self.assertHTMLEqual(
            str(
                html_parser(
                    """<div class="h-entry h-full h-feed h-card max-h-24">
                        <!-- strip any format of tailwindcss height utility -->
                        <span class="h-auto h-px h-full h-screen h-max h-min h-fit h-(--height) h-[2em] h-dvh h-dvw h-lvh h-lvw h-svh h-svw">
                            content about <code class="h-[1em] w-fit">h-full</code> utility
                        </span>
                    </div>"""
                )
            ),
            _html(
                """<div class="h-entry h-feed h-card max-h-24"><span>content about <code class="w-fit">h-full</code> utility</span></div>"""
            ),
        )
