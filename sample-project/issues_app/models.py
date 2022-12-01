from django.db import models
from django.urls import reverse
from issues_app.util import issue_url

from mentions.models.mixins import MentionableMixin


class IssueModel(models.Model):
    issue: int

    def issue_url(self):
        return issue_url(self.issue)

    class Meta:
        abstract = True


class Issue47Note(MentionableMixin, IssueModel):
    issue = 47

    text = models.TextField(blank=True)
    rss_only = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("issue-47-note", args=[self.pk])

    def get_content_html(self):
        return self.text
