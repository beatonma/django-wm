"""Views for debugging particular errors."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from issues_app.models import Issue47Note


class Issue47CreateNoteView(LoginRequiredMixin, CreateView):
    """https://github.com/beatonma/django-wm/issues/47"""

    model = Issue47Note
    template_name = "issues_app/47.html"
    fields = [
        "text",
        "rss_only",
        "allow_outgoing_webmentions",
    ]


class Issue47NoteView(TemplateView):
    template_name = "issues_app/47_note.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["note"] = Issue47Note.objects.get(id=kwargs["note_id"])
        return context
