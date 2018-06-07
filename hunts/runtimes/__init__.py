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
