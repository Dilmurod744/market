from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class NotLoginRequiredMixins(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('product_list')
        return super().dispatch(request, *args, **kwargs)