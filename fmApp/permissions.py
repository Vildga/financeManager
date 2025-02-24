from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Table


class IsTableOwnerMixin:

    def get_table(self):
        table = get_object_or_404(Table, id=self.kwargs.get("table_id"))
        if table.user != self.request.user:
            raise PermissionDenied
        return table
