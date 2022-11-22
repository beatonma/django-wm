from typing import Type

from django.db.models import Model
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views import View

from mentions import options, permissions
from mentions.models import (
    OutgoingWebmentionStatus,
    PendingIncomingWebmention,
    PendingOutgoingContent,
    Webmention,
)

__all__ = [
    "WebmentionDashboardView",
]


class WebmentionDashboardView(View):
    def get(self, request):
        if (
            not permissions.can_view_dashboard.has_perm(request.user)
            and not options.dashboard_public()
        ):
            return HttpResponseForbidden()

        def _sample(model_class: Type[Model]):
            return model_class.objects.all().order_by("-created_at")[:5]

        webmentions = _sample(Webmention)
        pending_incoming = _sample(PendingIncomingWebmention)
        pending_outgoing = _sample(PendingOutgoingContent)
        outgoing_statuses = _sample(OutgoingWebmentionStatus)

        return render(
            request,
            "mentions/webmention-dashboard.html",
            {
                "webmentions": webmentions,
                "pending_incoming": pending_incoming,
                "pending_outgoing": pending_outgoing,
                "outgoing_statuses": outgoing_statuses,
            },
        )
