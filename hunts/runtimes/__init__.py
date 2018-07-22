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


from hunts.runtimes.iframe import IFrameRuntime
from hunts.runtimes.lua import LuaRuntime
from hunts.runtimes.regex import RegexRuntime
from hunts.runtimes.static import StaticRuntime

IFRAME = 'I'
LUA    = 'L'
REGEX  = 'R'
STATIC = 'S'

RUNTIME_CHOICES = (
    (IFRAME, 'IFrame Runtime'),
    (LUA,    'Lua Runtime'),
    (REGEX,  'Regex Runtime'),
    (STATIC, 'Static Runtime'),
)


class Runtimes:
    runtimes = {
        IFRAME: IFrameRuntime,
        LUA:    LuaRuntime,
        REGEX:  RegexRuntime,
        STATIC: StaticRuntime,
    }

    def __getitem__(self, key):
        # Return an instantiated copy of the requested runtime
        return self.runtimes[key]()


runtimes = Runtimes()
