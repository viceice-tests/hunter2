from django import template
from ..resolvers import reverse

register = template.Library()

__all__ = (register, )


@register.simple_tag(takes_context=True)
def url(context, view, subdomain=None, *args, **kwargs):
    if subdomain is None:
        request = context.get('request')
        if request is not None:
            subdomain = getattr(request, 'subdomain', None)
        else:
            subdomain = None
    elif subdomain is '':
        subdomain = None

    return reverse(view, subdomain=subdomain, args=args, kwargs=kwargs)
