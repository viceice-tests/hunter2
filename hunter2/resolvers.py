from .settings import DEBUG

if DEBUG:
    from django.urls import reverse as django_reverse

    def reverse(*args, **kwargs):
        del kwargs['subdomain']
        return django_reverse(*args, **kwargs)
else:  # nocover
    from subdomains.utils import reverse

__all__ = (reverse, )
