# Settings for sample_app.
import os

DEFAULT_MENTION_TARGET_DOMAIN = os.environ.get("DEFAULT_MENTION_TARGET_DOMAIN") or ""
AUTOMENTION_EMABLED = os.environ.get("AUTOMENTION_ENABLED", "True").lower() == "true"
AUTOMENTION_URLS = [
    f"http://{DEFAULT_MENTION_TARGET_DOMAIN}{x}"
    for x in (os.environ.get("AUTOMENTION_URLS") or "").split(",")
]
# End of settings for sample_app
