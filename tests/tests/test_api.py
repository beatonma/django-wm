import inspect
from importlib import import_module
from types import ModuleType

from tests.tests.util.testcase import WebmentionTestCase


class ApiTestCase(WebmentionTestCase):
    """Checks for API consistency.

    All imports made with string names of the target object should bypass
    accidental changes by IDE-based refactoring - any name changes here should
    be done explicitly."""

    module_name: str

    def setUp(self):
        super().setUp()
        self.module = import_module(self.module_name)
        self.member_names = [x[0] for x in inspect.getmembers(self.module)]
        print(self.member_names)

    def assertModuleApiEqual(self, *obj_names: str):
        names = {x for x in self.member_names if "__" not in x}
        for obj_name in obj_names:
            self.assertTrue(
                obj_name in self.member_names,
                msg=f"Object '{obj_name}' not found in module '{self.module_name}'",
            )
            names.remove(obj_name)

        # Remove submodules from set of names
        module_names = set()
        for obj_name in names:
            obj = getattr(self.module, obj_name)
            if isinstance(obj, ModuleType):
                module_names.add(obj_name)

        names -= module_names

        # Remaining names (containing any exported classes, functions, etc) should be empty.
        self.assertEqual(
            0,
            len(names),
            msg=f"Unexpected exports from module '{self.module_name}': {names}",
        )

    def assertExistsInModule(self, *obj_names: str):
        for obj_name in obj_names:
            self.assertTrue(
                obj_name in self.member_names,
                msg=f"Object '{obj_name}' not found in module '{self.module_name}'",
            )

    def assertNotInModule(self, *obj_names: str):
        for obj_name in obj_names:
            self.assertFalse(
                obj_name in self.member_names,
                msg=f"Object '{obj_name}' should not be accessible in module '{self.module_name}'",
            )


class FormApiTests(ApiTestCase):
    module_name = "mentions.forms"

    def test_expected_forms_are_accessible(self):
        self.assertExistsInModule(
            "SubmitWebmentionForm",
        )


class HelperApiTests(ApiTestCase):
    module_name = "mentions.helpers"

    def test_expected_helpers_are_accessible(self):
        self.assertExistsInModule(
            "mentions_path",
            "mentions_re_path",
        )


class MiddlewareApiTests(ApiTestCase):
    module_name = "mentions.middleware"

    def test_expected_middleware_are_accessible(self):
        self.assertExistsInModule(
            "WebmentionHeadMiddleware",
        )


class MixinApiTests(ApiTestCase):
    module_name = "mentions.models.mixins"

    def test_expected_mixins_are_accessible(self):
        self.assertExistsInModule(
            "RetryableMixin",
            "MentionableMixin",
            "QuotableMixin",
        )


class ModelApiTests(ApiTestCase):
    module_name = "mentions.models"

    def test_expected_models_are_accessible(self):
        self.assertExistsInModule(
            "HCard",
            "OutgoingWebmentionStatus",
            "PendingIncomingWebmention",
            "PendingOutgoingContent",
            "SimpleMention",
            "Webmention",
        )

        self.assertNotInModule(
            "RetryableMixin",
            "MentionableMixin",
            "QuotableMixin",
        )


class TaskApiTests(ApiTestCase):
    module_name = "mentions.tasks"

    def test_expected_tasks_are_accessible(self):
        self.assertExistsInModule(
            "handle_pending_webmentions",
            "handle_incoming_webmention",
            "handle_outgoing_webmentions",
        )


class WagtailApiTests(ApiTestCase):
    module_name = "mentions.helpers.thirdparty.wagtail"

    def test_expected_wagtail_helpers_are_accessible(self):
        self.assertExistsInModule(
            "mentions_wagtail_path",
            "mentions_wagtail_re_path",
        )
