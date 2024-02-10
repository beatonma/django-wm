from typing import Optional, Set

from mentions.config import accept_domain_incoming, accept_domain_outgoing
from tests.tests.util import testfunc
from tests.tests.util.testcase import SimpleTestCase


class AcceptDomainIncomingTests(SimpleTestCase):
    """Tests for config.accept_domain_incoming with neither domains_allow, domains_deny defined."""

    def test_with_no_restrictions(self):
        self.assertTrue(
            accept_domain_incoming(
                testfunc.random_url(),
                None,
                None,
            )
        )


class AcceptDomainIncoming_withAllowList_Tests(SimpleTestCase):
    """Tests for config.accept_domain_incoming with domains_allow defined."""

    def _assertAllowed(self, url: str, domains_allow: Set[str]):
        self.assertTrue(
            accept_domain_incoming(url, domains_allow, None),
            msg=f"{url} not allowed by {domains_allow}",
        )

    def _assertNotAllowed(self, url: str, domains_allow: Set[str]):
        self.assertFalse(
            accept_domain_incoming(url, domains_allow, None),
            msg=f"{url} unexpectedly allowed by {domains_allow}",
        )

    def test_explicit_domains_are_accepted(self):
        allow = {"allow.org", "allow.com", "still.allow.net"}
        self._assertAllowed("https://allow.org", allow)
        self._assertAllowed("https://allow.com", allow)
        self._assertAllowed("https://still.allow.net/abc_", allow)
        self._assertAllowed("https://allow.org/whatever/123/?query=something", allow)

    def test_explicit_domains_are_not_accepted(self):
        allow = {"allow.org", "allow.com", "still.allow.net"}
        self._assertNotAllowed("https://not.allow.org", allow)
        self._assertNotAllowed(testfunc.random_url(), allow)

    def test_wildcard_domains_are_accepted(self):
        allow = {"*.allow.org", "*.allow.com", "*.still.allow.net"}
        self._assertAllowed("https://allow.org", allow)
        self._assertAllowed("https://allow.com", allow)
        self._assertAllowed(
            "https://also.still.allow.org/whatever/123/?query=something", allow
        )
        self._assertAllowed("https://still.allow.net", allow)
        self._assertAllowed("https://also.still.allow.net", allow)

    def test_wildcard_domains_are_not_accepted(self):
        allow = {"*.allow.org", "*.allow.com", "*.still.allow.net"}
        self._assertNotAllowed(testfunc.random_url(), allow)
        self._assertNotAllowed("https://notallow.org", allow)
        self._assertNotAllowed("https://*.notallow.org", allow)
        self._assertNotAllowed("https://other.allow.net", allow)

    def test_mixed_domains(self):
        allow = {"*.allow.org", "allow.com"}
        self._assertNotAllowed(testfunc.random_url(), allow)
        self._assertAllowed("https://allow.org", allow)
        self._assertAllowed("https://whatever.allow.org", allow)
        self._assertAllowed("https://allow.com", allow)
        self._assertNotAllowed("https://not.allow.com", allow)


class AcceptDomainIncoming_withDenyList_Tests(SimpleTestCase):
    """Tests for config.accept_domain_incoming with domains_deny defined."""

    def _assertDenied(self, url: str, domains_deny: Optional[Set[str]]):
        self.assertFalse(
            accept_domain_incoming(url, None, domains_deny),
            msg=f"{url} not denied by {domains_deny}",
        )

    def _assertNotDenied(self, url: str, domains_deny: Optional[Set[str]]):
        self.assertTrue(
            accept_domain_incoming(url, None, domains_deny),
            msg=f"{url} unexpectedly denied by {domains_deny}",
        )

    def test_explicit_domains_are_denied(self):
        deny = {"deny.org", "deny.com", "also.deny.net"}
        self._assertDenied("https://deny.org", deny)
        self._assertDenied("https://deny.com/whatever/123/?query=yes", deny)
        self._assertDenied("http://also.deny.net/nope/", deny)

    def test_explicit_domains_are_not_denied(self):
        deny = {"deny.org", "deny.com", "also.deny.net"}
        self._assertNotDenied(testfunc.random_url(), deny)
        self._assertNotDenied("https://other.deny.net", deny)

    def test_wildcard_domains_are_denied(self):
        deny = {"*.deny.org", "*.deny.com", "*.also.deny.net"}
        self._assertDenied("https://deny.org", deny)
        self._assertDenied("http://deny.com", deny)
        self._assertDenied("https://sub.deny.org", deny)
        self._assertDenied("https://also.deny.net/whatever/123/?query=something", deny)

    def test_wildcard_domains_are_not_denied(self):
        deny = {"*.deny.org", "*.deny.com", "*.also.deny.net"}
        self._assertNotDenied(testfunc.random_url(), deny)
        self._assertNotDenied("https://notdeny.org", deny)
        self._assertNotDenied("https://noalso.deny.net", deny)
        self._assertNotDenied("https://something.deny.net", deny)

    def test_mixed_domains(self):
        deny = {"*.deny.org", "deny.com"}
        self._assertDenied("https://deny.org", deny)
        self._assertDenied("https://sub.deny.org", deny)
        self._assertDenied("http://deny.com/a/b/c", deny)

        self._assertNotDenied("https://nodeny.org", deny)
        self._assertNotDenied("https://sub.deny.com", deny)


class AcceptDomainOutgoing(SimpleTestCase):
    """Tests for config.accept_domain_outgoing with neither domains_allow, domains_deny defined."""

    def test_with_no_restrictions(self):
        self.assertTrue(
            accept_domain_outgoing(
                testfunc.random_url(),
                True,
                None,
                None,
            )
        )


class AcceptDomainOutgoing_withAllowList_Tests(SimpleTestCase):
    def _assertAllowed(
        self,
        url: str,
        domains_allow: Set[str],
        allow_self_mention: bool = True,
    ):
        self.assertTrue(
            accept_domain_outgoing(
                url,
                allow_self_mention=allow_self_mention,
                domains_allow=domains_allow,
                domains_deny=None,
            ),
            msg=f"{url} not allowed by {domains_allow}",
        )

    def _assertNotAllowed(
        self,
        url: str,
        domains_allow: Set[str],
        allow_self_mention: bool = True,
    ):
        self.assertFalse(
            accept_domain_outgoing(
                url,
                allow_self_mention=allow_self_mention,
                domains_allow=domains_allow,
                domains_deny=None,
            ),
            msg=f"{url} unexpectedly allowed by {domains_allow}",
        )

    def test_explicit_domains_are_accepted(self):
        allow = {"allow.org", "allow.com", "also.allow.net"}
        self._assertAllowed("https://allow.org", allow)
        self._assertAllowed("http://allow.org/alfbda3", allow)
        self._assertAllowed("https://also.allow.net/asd2", allow)

    def test_explicit_domains_are_not_accepted(self):
        allow = {"allow.org", "allow.com", "also.allow.net"}
        self._assertNotAllowed(testfunc.random_url(), allow)
        self._assertNotAllowed("https://sub.allow.org", allow)
        self._assertNotAllowed("https://alsoallow.org", allow)

    def test_wildcard_domains_are_accepted(self):
        allow = {"*.allow.org", "*.allow.com", "*.also.allow.net"}
        self._assertAllowed("https://allow.org", allow)
        self._assertAllowed("http://allow.com/42", allow)
        self._assertAllowed("http://sub.allow.com/", allow)
        self._assertAllowed("https://a.a.allow.org/asdf123", allow)
        self._assertAllowed("https://also.allow.net/", allow)
        self._assertAllowed("http://a.also.allow.net/asdf123", allow)

    def test_wildcard_domains_are_not_accepted(self):
        allow = {"*.allow.org", "*.allow.com", "*.also.allow.net"}
        self._assertNotAllowed(testfunc.random_url(), allow)
        self._assertNotAllowed("https://fallow.org", allow)
        self._assertNotAllowed("https://not.allow.net", allow)


class AcceptDomainOutgoing_withDenyList_Tests(SimpleTestCase):
    def _assertDenied(
        self,
        url: str,
        domains_deny: Set[str],
        allow_self_mention: bool = True,
    ):
        self.assertFalse(
            accept_domain_outgoing(
                url,
                allow_self_mention=allow_self_mention,
                domains_allow=None,
                domains_deny=domains_deny,
            ),
            msg=f"{url} not denied by {domains_deny}",
        )

    def _assertNotDenied(
        self,
        url: str,
        domains_deny: Set[str],
        allow_self_mention: bool = True,
    ):
        self.assertTrue(
            accept_domain_outgoing(
                url,
                allow_self_mention=allow_self_mention,
                domains_allow=None,
                domains_deny=domains_deny,
            ),
            msg=f"{url} unexpectedly denied by {domains_deny}",
        )

    def test_explicit_domains_are_denied(self):
        deny = {"deny.org", "also.deny.net"}
        self._assertDenied("https://deny.org", deny)
        self._assertDenied("https://also.deny.net", deny)

    def test_explicit_domains_are_not_denied(self):
        deny = {"deny.org", "also.deny.net"}
        self._assertNotDenied(testfunc.random_url(), deny)
        self._assertNotDenied("https://sub.deny.org", deny)

    def test_wildcard_domains_are_denied(self):
        deny = {"*.deny.org", "*.also.deny.net"}
        self._assertDenied("https://deny.org/123", deny)
        self._assertDenied("https://sub.deny.org", deny)

    def test_wildcard_domains_are_not_denied(self):
        deny = {"*.deny.org", "*.also.deny.net"}
        self._assertNotDenied(testfunc.random_url(), deny)
        self._assertNotDenied("https://other.deny.net/123", deny)
