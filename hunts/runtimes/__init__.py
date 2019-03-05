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
        STATIC       = 'Static'
        CASED_STATIC = 'Case Sensitive Static'
        REGEX        = 'Regex'
        CASED_REGEX  = 'Case Sensitive Regex'
        IFRAME       = 'IFrame'
        LUA          = 'Lua'

    class Types:
        STATIC       = (StaticRuntime, {'case_sensitive': False}),
        CASED_STATIC = (StaticRuntime, {'case_sensitive': True}),
        REGEX        = (RegexRuntime, {'case_sensitive': False}),
        CASED_REGEX  = (RegexRuntime, {'case_sensitive': True}),
        IFRAME       = (IFrameRuntime, {}),
        LUA          = (LuaRuntime, {}),

    def __call__(self):
        _runtime = getattr(Runtime.Types, self)
        return _runtime[0](**_runtime[1])

    def is_printable(self):
        return self in (Runtime.CASED_REGEX, Runtime.CASED_STATIC, Runtime.REGEX, Runtime.STATIC)
