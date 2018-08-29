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
