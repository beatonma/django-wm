try:
    from mentions.models.mixins import IncomingMentionType, MentionableMixin
except ImportError:
    # django-wm<=2.3.0
    from mentions.models.mixins.mentionable import MentionableMixin

    class IncomingMentionType:
        def __members__(self):
            # Mock
            return {}
