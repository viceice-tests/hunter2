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


from enumfields import Enum


from .iframe import IFrameRuntime
from .lua import LuaRuntime
from .regex import RegexRuntime
from .static import StaticRuntime


class Runtime(Enum):
    CASED_REGEX  = 'r'
    CASED_STATIC = 's'
    IFRAME       = 'I'
    LUA          = 'L'
    REGEX        = 'R'
    STATIC       = 'S'

    class Labels:
        CASED_REGEX  = 'Case Sensitive Regex'
        CASED_STATIC = 'Case Sensitive Static'
        IFRAME       = 'IFrame'
        LUA          = 'Lua'
        REGEX        = 'Regex'
        STATIC       = 'Static'

    class Options:
        CASED_REGEX = {'case_sensitive': True}
        CASED_STATIC = {'case_sensitive': True}
        REGEX = {'case_sensitive': False}
        STATIC = {'case_sensitive': False}

    class Types:
        STATIC       = StaticRuntime
        CASED_STATIC = StaticRuntime
        REGEX        = RegexRuntime
        CASED_REGEX  = RegexRuntime
        IFRAME       = IFrameRuntime
        LUA          = LuaRuntime

    def __call__(self):
        Type = getattr(Runtime.Types, self.name)
        try:
            options = getattr(Runtime.Options, self.name)
        except AttributeError:
            options = {}
        return Type(**options)

    def is_printable(self):
        return self in (Runtime.CASED_REGEX, Runtime.CASED_STATIC, Runtime.REGEX, Runtime.STATIC)
