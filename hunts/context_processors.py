# Copyright (C) 2018 The Hunter2 Contributors.
#
# This file is part of Hunter2.
#
# Hunter2 is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Hunter2 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with Hunter2.  If not, see <http://www.gnu.org/licenses/>.


from django.db.models import Q

from hunts import models


def announcements(request):
    # Announcements are stored in tenant schemas. Some views won't have these in the search path.
    if request.tenant is None:
        return {}

    # Get all announcements, including puzzle specific announcements if present
    has_puzzle = hasattr(request, 'puzzle') and request.puzzle is not None

    if has_puzzle:
        current_announcements = models.Announcement.objects.filter(
            (Q(event__isnull=True) | Q(event=request.tenant)) &
            (Q(puzzle__isnull=True) | Q(puzzle=request.puzzle)))
    else:
        current_announcements = models.Announcement.objects.filter(
            (Q(event__isnull=True) | Q(event=request.tenant)) &
            (Q(puzzle__isnull=True)))

    if request.user.is_authenticated and request.user.info.attendance_at(request.tenant).seat == '':
        no_seat = models.Announcement(
            id='no-seat-announcement',
            event=request.tenant,
            title='No Seat Set',
            message="You don't have a seat set at this event. Set your seat on the account page.",
            type=models.AnnouncementType.WARNING,
        )
        no_seat.special = True
        current_announcements = list(current_announcements) + [no_seat]

    return {
        'announcements': current_announcements
    }
