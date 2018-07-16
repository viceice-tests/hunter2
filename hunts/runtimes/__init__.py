# vim: set fileencoding=utf-8 :
from hunts.runtimes.iframe import IFrameRuntime
from hunts.runtimes.lua import LuaRuntime
from hunts.runtimes.regex import RegexRuntime
from hunts.runtimes.static import StaticRuntime

CASED_REGEX  = 'r'
CASED_STATIC = 's'
IFRAME       = 'I'
LUA          = 'L'
REGEX        = 'R'
STATIC       = 'S'

RUNTIME_CHOICES = (
    (STATIC,       'Static Runtime'),
    (CASED_STATIC, 'Case Sensitive Static Runtime'),
    (REGEX,        'Regex Runtime'),
    (CASED_REGEX,  'Case Sensitive Regex Runtime'),
    (IFRAME,       'IFrame Runtime'),
    (LUA,          'Lua Runtime'),
)


class Runtimes:
    runtimes = {
        CASED_REGEX:  (RegexRuntime, {'case_sensitive': True}),
        CASED_STATIC: (StaticRuntime, {'case_sensitive': True}),
        IFRAME:       (IFrameRuntime, {}),
        LUA:          (LuaRuntime, {}),
        REGEX:        (RegexRuntime, {'case_sensitive': False}),
        STATIC:       (StaticRuntime, {'case_sensitive': False}),
    }

    def __getitem__(self, key):
        # Return an instantiated copy of the requested runtime
        entry = self.runtimes[key]
        return entry[0](**entry[1])


runtimes = Runtimes()
