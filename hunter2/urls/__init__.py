from ..settings import DEBUG

if DEBUG:
    from .admin import urlpatterns as admin_patterns
    from .www import urlpatterns as www_patterns

    urlpatterns = admin_patterns + www_patterns
else:
    urlpatterns = []
