# Base URL path (global urlpatterns)
namespace = 'webmention'

model_name = 'tests.MentionableTestModel'

unmentionable_view = 'unmentionable_view'
http_header_view = 'http_header_view'
html_head_view = 'html_head_view'
html_anchor_view = 'html_anchor_view'
all_endpoints_view = 'all_endpoints_view'

# Path as configured in the local urlpatterns
correct_config = 'with_correct_config'
