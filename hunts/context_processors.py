from django.db.models import Q

from hunts import models
from hunts.models import AnnoucmentType


def announcements(request):

    # Get all announcements, including puzzle specific announcements if present
    has_puzzle = hasattr(request, 'puzzle') and request.puzzle is not None

    if has_puzzle:
        current_announcements = models.Annoucement.objects.filter(
            (Q(event__isnull=True) | Q(event=request.event)) &
            (Q(puzzle__isnull=True) | Q(puzzle=request.puzzle)))
    else:
        current_announcements = models.Annoucement.objects.filter(
            (Q(event__isnull=True) | Q(event=request.event)) &
            (Q(puzzle__isnull=True)))

    # TODO: This is relatively closely linked to the CSS so perhaps should be further moved to the view / template
    for announcement in current_announcements:
        if announcement.type == AnnoucmentType.INFO:
            announcement.css_type = 'alert-info'
        elif announcement.type == AnnoucmentType.SUCCESSS:
            announcement.css_type = 'alert-success'
        elif announcement.type == AnnoucmentType.WARNING:
            announcement.css_type = 'alert-warning'
        elif announcement.type == AnnoucmentType.ERROR:
            announcement.css_type = 'alert-danger'

    return {
        'announcements': current_announcements
    }
