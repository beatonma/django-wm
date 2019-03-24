"""Constants that are used in several separate tests."""

namespace = 'webmention'

"""Dotted name of the model used for testing."""
model_name = 'tests.MentionableTestModel'

# Path as configured in the local urlpatterns
correct_config = 'with_correct_config'

slug_regex = r'(?P<slug>[\w\-.]+)/?$'
