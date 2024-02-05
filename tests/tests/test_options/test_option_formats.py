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

        settings.WEBMENTIONS_USE_CELERY = False
        settings.WEBMENTIONS_AUTO_APPROVE = True
        settings.WEBMENTIONS_URL_SCHEME = "http"
        settings.WEBMENTIONS_TIMEOUT = 20
        settings.WEBMENTIONS_MAX_RETRIES = 25
        settings.WEBMENTIONS_RETRY_INTERVAL = 30
        settings.WEBMENTIONS_DASHBOARD_PUBLIC = True
        settings.WEBMENTIONS_INCOMING_TARGET_MODEL_REQUIRED = True
        settings.WEBMENTIONS_ALLOW_SELF_MENTIONS = False
        settings.WEBMENTIONS_DEFAULT_URL_PARAMETER_MAPPING = {"foo": "bar"}
        settings.WEBMENTIONS_ALLOW_OUTGOING_DEFAULT = False
        settings.WEBMENTIONS_INCLUDE_DOMAINS = {"include"}
        settings.WEBMENTIONS_EXCLUDE_DOMAINS = {"exclude"}

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
        self.assertSetEqual(options.included_domains(), {"include"})
        self.assertSetEqual(options.excluded_domains(), {"exclude"})

    def test_namespaced_settings(self):
        from django.conf import settings

        settings.WEBMENTIONS = {
            "USE_CELERY": True,
            "AUTO_APPROVE": False,
            "URL_SCHEME": "https",
            "TIMEOUT": 21,
            "MAX_RETRIES": 26,
            "RETRY_INTERVAL": 31,
            "DASHBOARD_PUBLIC": False,
            "INCOMING_TARGET_MODEL_REQUIRED": False,
            "ALLOW_SELF_MENTIONS": True,
            "DEFAULT_URL_PARAMETER_MAPPING": {"bar": "foo"},
            "ALLOW_OUTGOING_DEFAULT": True,
            "INCLUDE_DOMAINS": ("included",),
            "EXCLUDE_DOMAINS": ["excluded"],
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
        self.assertTupleEqual(options.included_domains(), ("included",))
        self.assertListEqual(options.excluded_domains(), ["excluded"])
