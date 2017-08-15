from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from teams.models import UserProfile
from . import models


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(m2m_changed, sender=models.Team.members.through)
def members_changed(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_add':
        if instance.is_full():
            raise ValidationError('Teams can have at most %d members' % instance.at_event.max_team_size)
        for user_id in pk_set:
            user = models.UserProfile.objects.get(pk=user_id)
            if models.Team.objects.exclude(pk=instance.pk).filter(at_event=instance.at_event).filter(members=user).count() > 0:
                pk_set.remove(user_id)
                raise ValidationError('User can only join one team per same event')
