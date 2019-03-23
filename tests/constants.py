# Base URL path (global urlpatterns)
from dataclasses import dataclass

namespace = 'webmention'

model_name = 'tests.MentionableTestModel'


@dataclass
class Views:
    unmentionable = 'unmentionable_view'
    http_header = 'http_header_view'
    html_head = 'html_head_view'
    html_anchor = 'html_anchor_view'
    all_endpoints = 'all_endpoints_view'


views = Views()


# views = {
#     'unmentionable': 'unmentionable_view',
#     'http_header': 'http_header_view',
#     'html_head': 'html_head_view',
#     'html_anchor': 'html_anchor_view',
#     'all_endpoints': 'all_endpoints_view',
# }

# Path as configured in the local urlpatterns
correct_config = 'with_correct_config'
