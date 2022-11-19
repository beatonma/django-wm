from mentions import options
from tests.tests.util.testcase import OptionsTestCase


class FlatSettingsTests(OptionsTestCase):
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

        self.assertFalse(options.use_celery())
        self.assertTrue(options.auto_approve())
        self.assertEqual(options.url_scheme(), "http")
        self.assertEqual(options.timeout(), 20)
        self.assertEqual(options.max_retries(), 25)
        self.assertEqual(options.retry_interval(), 30)
        self.assertTrue(options.dashboard_public())
        self.assertTrue(options.target_requires_model())
        self.assertFalse(options.allow_self_mentions())
        self.assertDictEqual(options.default_url_parameter_mapping(), dict(foo="bar"))

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
        self.assertDictEqual(options.default_url_parameter_mapping(), dict(bar="foo"))
