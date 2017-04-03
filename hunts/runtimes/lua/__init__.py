# vim: set fileencoding=utf-8 :
import os

import lupa

from .. import (
    AbstractRuntime, RuntimeExecutionError, RuntimeExecutionTimeExceededError,
    RuntimeMemoryExceededError,
)


class LuaRuntime(AbstractRuntime):
    ERROR_INSTRUCTION_LIMIT_EXCEEDED = "ERROR_INSTRUCTION_LIMIT_EXCEEDED"
    ERROR_MEMORY_LIMIT_EXCEEDED      = "ERROR_MEMORY_LIMIT_EXCEEDED"

    def __init__(self):
        pass

    def evaluate(self, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        return_values = self._sandbox_run(script)
        # TODO: Make checking for number of return parameters more robust
        if len(return_values) == 0:
            raise RuntimeExecutionError("Lua script did not return a value")
        return return_values[0]

    def validate_guess(self, validator, guess, team_puzzle_data, team_data):
        return_values = self._sandbox_run(validator)
        # TODO: Make checking for number of return parameters more robust
        if len(return_values) == 0:
            raise RuntimeExecutionError("Lua script did not return a value")
        return return_values[0]

    @staticmethod
    def _python_attribute_getter(obj, attr_name):
        raise AttributeError("Attribute access disabled in sandbox")

    @staticmethod
    def _python_attribute_setter(attr_name, value):
        raise AttributeError("Attribute access disabled in sandbox")

    def _create_lua_runtime(self):
        # noinspection PyArgumentList
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

    def _sandbox_run(self, lua_script):
        lua = self._create_lua_runtime()

        # Load the sandbox Lua module
        sandbox = lua.require('sandbox')

        # The 'result' object here can be either a bool or a tuple depending on
        # the result of the Lua function, the following results are possible:
        #  - True:           script succeeded but returned nothing
        #  - (True, ...):    script succeeded with return values
        #  - (False, error): script raised an error during execution
        #  - (None, error):  script syntax loading error
        try:
            result = sandbox.run(lua_script)
            # If just a bool, return the empty result for success
            if isinstance(result, bool) and result is True:
                return []

            # Check result of executing the Lua script
            if result[0] is not True:
                exit_status, error = result

                if exit_status is None:
                    raise SyntaxError(error)

                if exit_status is False:
                    if str(error).endswith(self.ERROR_INSTRUCTION_LIMIT_EXCEEDED):
                        raise RuntimeExecutionTimeExceededError()
                    elif str(error).endswith(self.ERROR_MEMORY_LIMIT_EXCEEDED):
                        raise RuntimeMemoryExceededError()
                    else:
                        raise RuntimeExecutionError(error)
            else:
                # Expand the return values to a list and return
                exit_status, *return_values = result
                return return_values

        except lupa.LuaError as error:
            # An error has occurred in the sandbox runtime itself
            raise RuntimeExecutionError("Sandbox") from error
