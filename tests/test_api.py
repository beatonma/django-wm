import inspect
from importlib import import_module

from tests import WebmentionTestCase


class ApiTestCase(WebmentionTestCase):
    module_name: str

    def setUp(self):
        super().setUp()
        _module = import_module(self.module_name)
        self.member_names = [x[0] for x in inspect.getmembers(_module)]

    def assertExistsInModule(self, obj_name: str):
        self.assertTrue(
            obj_name in self.member_names,
            msg=f"Object '{obj_name}' not found in module '{self.module_name}'",
        )


class ModelApiTests(ApiTestCase):
    module_name = "mentions.models"

    def test_expected_models_are_accessible(self):
        self.assertExistsInModule("HCard")
        self.assertExistsInModule("OutgoingWebmentionStatus")
        self.assertExistsInModule("PendingIncomingWebmention")
        self.assertExistsInModule("PendingOutgoingContent")
        self.assertExistsInModule("SimpleMention")
        self.assertExistsInModule("Webmention")


class MiddlewareApiTests(ApiTestCase):
    module_name = "mentions.middleware"

    def test_expected_middleware_are_accessible(self):
        self.assertExistsInModule("WebmentionHeadMiddleware")


class FormApiTests(ApiTestCase):
    module_name = "mentions.forms"

    def test_expected_forms_are_accessible(self):
        self.assertExistsInModule("SubmitWebmentionForm")


class MixinApiTests(ApiTestCase):
    module_name = "mentions.models.mixins"

    def test_expected_mixins_are_accessible(self):
        self.assertExistsInModule("RetryableMixin")
        self.assertExistsInModule("MentionableMixin")
        self.assertExistsInModule("QuotableMixin")


class TaskApiTests(ApiTestCase):
    module_name = "mentions.tasks"

    def test_expected_tasks_are_accessible(self):
        self.assertExistsInModule("handle_incoming_webmention")
        self.assertExistsInModule("handle_outgoing_webmentions")
        self.assertExistsInModule("handle_pending_webmentions")


class ViewApiTests(ApiTestCase):
    module_name = "mentions.views"

    def test_expected_views_are_accessible(self):
        self.assertExistsInModule("GetMentionsView")
        self.assertExistsInModule("WebmentionView")
        self.assertExistsInModule("WebmentionDashboardView")
