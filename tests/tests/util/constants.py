"""Constants that are used in several tests."""
import uuid

"""The root path for mentions.urls.
Generated randomly at test runtime as user may include(mentions.urls) to point to any location."""
namespace = uuid.uuid4().hex

"""Dotted name of the model used for testing."""
model_name = "test_app.MentionableTestModel"
model_name_test_blogpost = "test_app.MentionableTestBlogPost"
