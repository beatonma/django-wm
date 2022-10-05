from mentions.tasks.outgoing import local, remote
from tests import MockResponse, WebmentionTestCase
from tests.util import snippets, testfunc

OUTGOING_WEBMENTION_HTML_DUPLICATE_LINKS = f"""<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://beatonma.org/">This is a mentionable link</a> 
blah blah duplicate links
<a href="https://snommoc.org/">This is some other link</a> 
<a href="https://beatonma.org/">This is a duplicate link</a> 
</body></html>
"""

OUTGOING_WEBMENTION_HTML_SELF_LINKS = f"""<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://beatonma.org/">This is a mentionable link</a> 
aesjfgkljasn <a href="#contents">Link to self #ID</a> 
</body></html>
"""


class EndpointDiscoveryTests(WebmentionTestCase):
    """OUTGOING: Endpoint discovery & resolution."""

    absolute_endpoint = testfunc.endpoint_submit_webmention_absolute()
    relative_endpoint = testfunc.endpoint_submit_webmention()

    def setUp(self):
        self.target = testfunc.create_mentionable_object()

    def _get_absolute_target_url(self):
        return testfunc.get_absolute_url_for_object(self.target)

    def test_get_absolute_endpoint_from_response(self):
        """Any exposed endpoints (in HTTP header, HTML <head> or <body>) are found and returned as an absolute url."""
        func = remote._get_absolute_endpoint_from_response
        mock_response = MockResponse(
            url=self._get_absolute_target_url(),
            headers={"Link": snippets.http_link_endpoint()},
        )
        absolute_endpoint_from_http_headers = func(mock_response)
        self.assertEqual(self.absolute_endpoint, absolute_endpoint_from_http_headers)

        mock_response.headers = {}
        mock_response.text = snippets.html_head_endpoint()
        absolute_endpoint_from_html_head = func(mock_response)
        self.assertEqual(self.absolute_endpoint, absolute_endpoint_from_html_head)

        mock_response.headers = {}
        mock_response.text = snippets.html_body_endpoint()
        absolute_endpoint_from_html_body = func(mock_response)
        self.assertEqual(self.absolute_endpoint, absolute_endpoint_from_html_body)

    def test_get_endpoint_in_http_headers(self):
        """Endpoints exposed in HTTP header are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(),
            headers={"Link": snippets.http_link_endpoint()},
        )
        endpoint_from_http_headers = remote.get_endpoint_in_http_headers(
            mock_response.headers
        )
        self.assertEqual(self.relative_endpoint, endpoint_from_http_headers)

    def test_get_endpoint_in_html_head(self):
        """Endpoints exposed in HTML <head> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(),
            text=snippets.html_head_endpoint(),
        )
        endpoint_from_html_head = remote.get_endpoint_in_html(mock_response.text)
        self.assertEqual(self.relative_endpoint, endpoint_from_html_head)

    def test_get_endpoint_in_html_body(self):
        """Endpoints exposed in HTML <body> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(),
            text=snippets.html_body_endpoint(),
        )
        endpoint_from_html_body = remote.get_endpoint_in_html(mock_response.text)
        self.assertEqual(self.relative_endpoint, endpoint_from_html_body)

    def test_relative_to_absolute_url(self):
        """Relative URLs are correctly converted to absolute URLs."""

        func = remote._relative_to_absolute_url

        domain = testfunc.random_domain()
        base_url = f"https://{domain}"
        page_url = f"{base_url}/some/url/path"
        response = MockResponse(url=page_url)

        self.assertEqual(
            f"https://{domain}/webmention/",
            func(response, "/webmention/"),
        )

        self.assertEqual(
            f"https://{domain}/some/url/webmention/",
            func(response, "webmention/"),
        )

        self.assertEqual(
            f"https://{domain}/already_absolute_path",
            func(response, f"https://{domain}/already_absolute_path"),
        )

    def test_get_target_links_in_text(self):
        """Outgoing links are found correctly."""

        urls = {
            f"https://{testfunc.random_domain()}",
            f"http://{testfunc.random_domain()}/some-path",
            f"https://{testfunc.random_domain()}/some-path/something_else_04/",
            f"https://subdomain.{testfunc.random_domain()}/blah-blah/",
            *{testfunc.random_url() for _ in range(0, 5)},
        }

        outgoing_content = "".join(
            [
                f'This is some content that mentions <a href="{url}">this page</a>.'
                for url in urls
            ]
        )

        outgoing_links = local.get_target_links_in_html(outgoing_content, "/")
        self.assertSetEqual(urls, outgoing_links)

    def test_get_target_links_in_text__ignores_self_anchors(self):
        """_get_target_links_in_text should remove any links that target the source page."""

        outgoing_links = local.get_target_links_in_html(
            OUTGOING_WEBMENTION_HTML_SELF_LINKS, "/"
        )

        self.assertSetEqual({"https://beatonma.org/"}, outgoing_links)
