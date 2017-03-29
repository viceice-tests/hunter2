# vim: set fileencoding=utf-8 :
import os
import lupa

from hunts.runtimes import AbstractRuntime

class LuaRuntime(AbstractRuntime):
    def __init__(self):
        self._lua = self._create_lua_runtime()

    def evaluate(self, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        sandbox = self._lua.require('sandbox')
        result = sandbox.run(script)
        # TODO: Make checking for number of return parameters more robust
        if result is False:
            _, error = result
            raise lupa.LuaError(error)
        else:
            _, value = result
            return value

    def validate_guess(self, validator, guess, team_puzzle_data, team_data):
        sandbox = self._lua.require('sandbox')
        result = sandbox.run(validator)
        # TODO: Make checking for number of return parameters more robust
        if result is False:
            _, error = result
            raise lupa.LuaError(error)
        else:
            _, correct = result
            return correct

    @staticmethod
    def _python_attribute_getter(obj, attr_name):
        raise AttributeError("Attribute access disabled in sandbox")

    @staticmethod
    def _python_attribute_setter(attr_name, value):
        raise AttributeError("Attribute access disabled in sandbox")

    def _create_lua_runtime(self):
        lua = lupa.LuaRuntime(
            register_eval=False,
            register_builtins=False,
            unpack_returned_tuples=True,
            attribute_handlers=(
                self._python_attribute_getter,
                self._python_attribute_setter
            )
        )
        lua.execute("assert(os.setlocale('C'))")
        lua.globals().package.path = os.path.join(os.path.dirname(__file__), "?.lua")
        return lua