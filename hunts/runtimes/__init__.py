# vim: set fileencoding=utf-8 :
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

RUNTIMES = {
    IFRAME: IFrameRuntime,
    LUA:    LuaRuntime,
    REGEX:  RegexRuntime,
    STATIC: StaticRuntime,
}
