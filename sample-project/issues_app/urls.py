from django.urls import path
from issues_app.views import Issue47CreateNoteView, Issue47NoteView

urlpatterns = [
    path("47/", Issue47CreateNoteView.as_view()),
    path("47/note/<int:note_id>", Issue47NoteView.as_view(), name="issue-47-note"),
]
