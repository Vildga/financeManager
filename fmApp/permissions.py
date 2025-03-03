from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Table

from django.http import Http404


class IsTableOwnerMixin:
    def dispatch(self, request, *args, **kwargs):
        table_id = kwargs.get("table_id")
        table = get_object_or_404(Table, pk=table_id)

        if table.user != request.user:
            raise Http404("Table not found")  # або 403

        return super().dispatch(request, *args, **kwargs)
