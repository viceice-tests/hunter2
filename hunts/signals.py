from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from . import models


@receiver(m2m_changed, sender=models.Episode.prequels.through)
def members_changed(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_add':
        for episode_id in pk_set:
            episode = models.Episode.objects.get(pk=episode_id)
            if episode == instance:
                raise ValidationError('Episode cannot follow itself')
            elif episode.follows(instance):
                raise ValidationError('Circular dependency found in episodes')
