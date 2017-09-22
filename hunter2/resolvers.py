from . import settings

if settings.DEBUG:
    from subdomains.utils import reverse as subdomain_reverse

    def reverse(*args, **kwargs):
        del kwargs['subdomain']
        return subdomain_reverse(*args, **kwargs)
else:
    from subdomains.utils import reverse

__all__ = (reverse, )
