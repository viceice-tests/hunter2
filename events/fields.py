from django.db.models import BooleanField


class SingleTrueBooleanField(BooleanField):

    def pre_save(self, model_instance, add):
        objects = model_instance.__class__.objects

        # Ensure all others are false if this value is True
        if getattr(model_instance, self.attname):
            objects.update(**{self.attname: False})

        # If none is set as true, ensure this one is set as True
        elif not objects.exclude(id=model_instance.id).filter(**{self.attname: True}):
            setattr(model_instance, self.attname, True)

        return getattr(model_instance, self.attname)
