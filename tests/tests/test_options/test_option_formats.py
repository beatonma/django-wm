from mentions import options
from tests.tests.util.testcase import OptionsTestCase


class FlatSettingsTests(OptionsTestCase):
    """Ensure that all settings can be read correctly in flat or namespaced format:
    - WEBMENTIONS_SETTING_NAME = "value"
    - WEBMENTIONS = {
        "SETTING_NAME": "value
    }
    """

    def test_flat_settings(self):
        from django.conf import settings

        settings.WEBMENTIONS_ALLOW_OUTGOING_DEFAULT = False
        settings.WEBMENTIONS_ALLOW_SELF_MENTIONS = False
        settings.WEBMENTIONS_AUTO_APPROVE = True
        settings.WEBMENTIONS_DASHBOARD_PUBLIC = True
        settings.WEBMENTIONS_DEFAULT_URL_PARAMETER_MAPPING = {"foo": "bar"}
        settings.WEBMENTIONS_DOMAINS_OUTGOING_ALLOW = {"include"}
        settings.WEBMENTIONS_DOMAINS_OUTGOING_DENY = {"exclude"}
        settings.WEBMENTIONS_DOMAINS_OUTGOING_TAG_ALLOW = "wm-send"
        settings.WEBMENTIONS_DOMAINS_OUTGOING_TAG_DENY = "wm-nosend"
        settings.WEBMENTIONS_INCOMING_TARGET_MODEL_REQUIRED = True
        settings.WEBMENTIONS_MAX_RETRIES = 25
        settings.WEBMENTIONS_RETRY_INTERVAL = 30
        settings.WEBMENTIONS_TIMEOUT = 20
        settings.WEBMENTIONS_URL_SCHEME = "http"
        settings.WEBMENTIONS_USE_CELERY = False
        settings.WEBMENTIONS_USER_AGENT = "empty"

        self.assertFalse(options.use_celery())
        self.assertTrue(options.auto_approve())
        self.assertEqual(options.url_scheme(), "http")
        self.assertEqual(options.timeout(), 20)
        self.assertEqual(options.max_retries(), 25)
        self.assertEqual(options.retry_interval(), 30)
        self.assertTrue(options.dashboard_public())
        self.assertTrue(options.target_requires_model())
        self.assertFalse(options.allow_self_mentions())
        self.assertFalse(options.allow_outgoing_default())
        self.assertDictEqual(options.default_url_parameter_mapping(), dict(foo="bar"))
        self.assertSetEqual(options.outgoing_domains_allow(), {"include"})
        self.assertSetEqual(options.outgoing_domains_deny(), {"exclude"})
        self.assertEqual(options.outgoing_domains_tag_allow(), "wm-send")
        self.assertEqual(options.outgoing_domains_tag_deny(), "wm-nosend")
        self.assertEqual(options.user_agent(), "empty")

    def test_namespaced_settings(self):
        from django.conf import settings

        settings.WEBMENTIONS = {
            "ALLOW_OUTGOING_DEFAULT": True,
            "ALLOW_SELF_MENTIONS": True,
            "AUTO_APPROVE": False,
            "DASHBOARD_PUBLIC": False,
            "DEFAULT_URL_PARAMETER_MAPPING": {"bar": "foo"},
            "DOMAINS_OUTGOING_ALLOW": ("included",),
            "DOMAINS_OUTGOING_DENY": ["excluded"],
            "DOMAINS_OUTGOING_TAG_ALLOW": "send-wm",
            "DOMAINS_OUTGOING_TAG_DENY": "nosend-wm",
            "INCOMING_TARGET_MODEL_REQUIRED": False,
            "MAX_RETRIES": 26,
            "RETRY_INTERVAL": 31,
            "TIMEOUT": 21,
            "URL_SCHEME": "https",
            "USE_CELERY": True,
            "USER_AGENT": "nope",
        }

        self.assertTrue(options.use_celery())
        self.assertFalse(options.auto_approve())
        self.assertEqual(options.url_scheme(), "https")
        self.assertEqual(options.timeout(), 21)
        self.assertEqual(options.max_retries(), 26)
        self.assertEqual(options.retry_interval(), 31)
        self.assertFalse(options.dashboard_public())
        self.assertFalse(options.target_requires_model())
        self.assertTrue(options.allow_self_mentions())
        self.assertTrue(options.allow_outgoing_default())
        self.assertDictEqual(options.default_url_parameter_mapping(), dict(bar="foo"))
        self.assertSetEqual(options.outgoing_domains_allow(), {"included"})
        self.assertSetEqual(options.outgoing_domains_deny(), {"excluded"})
        self.assertEqual(options.outgoing_domains_tag_allow(), "send-wm")
        self.assertEqual(options.outgoing_domains_tag_deny(), "nosend-wm")
        self.assertEqual(options.user_agent(), "nope")
