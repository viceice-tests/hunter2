from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from . import models


@receiver(m2m_changed, sender=models.Episode.puzzles.through)
def episode_puzzles_changed(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_add':
        for puzzle_id in pk_set:
            puzzle = models.Puzzle.objects.get(pk=puzzle_id)
            if puzzle.episode_set.count() > 0:
                raise ValidationError('Puzzle can only be used in one episode')

@receiver(m2m_changed, sender=models.Episode.prequels.through)
def episode_prequels_changed(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_add':
        for episode_id in pk_set:
            episode = models.Episode.objects.get(pk=episode_id)
            if episode == instance:
                raise ValidationError('Episode cannot follow itself')
            elif episode.follows(instance):
                raise ValidationError('Circular dependency found in episodes')
