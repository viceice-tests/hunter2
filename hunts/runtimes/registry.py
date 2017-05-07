# vim: set fileencoding=utf-8 :
from hunts.runtimes.lua import LuaRuntime
from hunts.runtimes.regex import RegexRuntime
from hunts.runtimes.static import StaticRuntime


class RuntimesRegistry(object):
    STATIC = 'S'
    LUA    = 'L'
    REGEX  = 'R'

    RUNTIME_CHOICES = (
        (STATIC, 'Static Runtime'),
        (LUA,    'Lua Runtime'),
        (REGEX,  'Regex Run'),
    )

    REGISTERED_RUNTIMES = {
        STATIC: StaticRuntime(),
        LUA:    LuaRuntime(),
        REGEX:  RegexRuntime(),
    }

    @staticmethod
    def evaluate(runtime, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        return RuntimesRegistry.REGISTERED_RUNTIMES[runtime].evaluate(
            script,
            team_puzzle_data=team_puzzle_data,
            user_puzzle_data=user_puzzle_data,
            team_data=team_data,
            user_data=user_data,
        )

    @staticmethod
    def validate_guess(runtime, script, guess, team_puzzle_data, team_data):
        return RuntimesRegistry.REGISTERED_RUNTIMES[runtime].validate_guess(
            script,
            guess,
            team_puzzle_data=team_puzzle_data,
            team_data=team_data,
        )
