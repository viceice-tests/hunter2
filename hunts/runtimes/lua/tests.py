# vim: set fileencoding=utf-8 :
from unittest import TestCase

from parameterized import parameterized

from .. import RuntimeExecutionError, RuntimeExecutionTimeExceededError, RuntimeMemoryExceededError, RuntimeSandboxViolationError
from . import LuaRuntime


class LuaRuntimeTestCase(TestCase):
    def test_evaluate(self):
        lua_runtime = LuaRuntime()
        lua_script = '''return "Hello World"'''
        result = lua_runtime.evaluate(lua_script, None, None, None, None)
        self.assertEqual(result, "Hello World")

    def test_evaluate_requires_return_value(self):
        lua_runtime = LuaRuntime()
        lua_script = ''''''
        with self.assertRaises(RuntimeExecutionError):
            lua_runtime.evaluate(lua_script, None, None, None, None)

    def test_validate_guess(self):
        lua_runtime = LuaRuntime()
        lua_script = '''return (tonumber(guess) == 100 + 100)'''
        guess = "200"
        result = lua_runtime.validate_guess(lua_script, guess, None, None)
        self.assertTrue(result, "Guess was correct, but did not return true")

    def test_validate_guess_requires_return_value(self):
        lua_runtime = LuaRuntime()
        lua_script = ''''''
        with self.assertRaises(RuntimeExecutionError):
            lua_runtime.validate_guess(lua_script, None, None, None)

    def test_evaluate_syntax_error_fails(self):
        lua_runtime = LuaRuntime()
        lua_script = '''@'''
        with self.assertRaises(SyntaxError):
            lua_runtime.evaluate(lua_script, None, None, None, None)

    def test_evaluate_error_fails(self):
        lua_runtime = LuaRuntime()
        lua_script = '''error("error_message")'''
        with self.assertRaises(RuntimeExecutionError) as context:
            lua_runtime.evaluate(lua_script, None, None, None, None)
        self.assertRegex(context.exception.message, ".*error_message$")


class LuaSandboxTestCase(TestCase):
    # Functions that we do not want to expose to our sandbox
    PROTECTED_FUNCTIONS = [
        'collectgarbage',
        'dofile',
        'load',
        'loadfile',
        'coroutine',
        'debug',
        'io',
        'os.date',
        'os.execute',
        'os.exit',
        'os.getenv',
        'os.remove',
        'os.rename',
        'os.setlocale',
        'os.tmpname',
        'package',
        'string.dump',
    ]

    @parameterized.expand(PROTECTED_FUNCTIONS)
    def test_lua_sandbox_disabled(self, unsafe_function):
        lua_runtime = LuaRuntime()
        lua_script = '''return {} == nil'''.format(unsafe_function)
        result = lua_runtime._sandbox_run(lua_script)[0]
        self.assertTrue(result, "Lua function {} is accessible in sandbox".format(unsafe_function))

    def test_lua_sandbox_instruction_limit(self):
        lua_runtime = LuaRuntime()
        lua_script = '''for i=1,100000 do i=i end'''
        with self.assertRaises(RuntimeExecutionTimeExceededError):
            lua_runtime._sandbox_run(lua_script, instruction_limit=100)

    def test_lua_sandbox_memory_limit(self):
        lua_runtime = LuaRuntime()
        lua_script = '''t = {} for i=1,10000 do t[i] = i end'''
        with self.assertRaises(RuntimeMemoryExceededError):
            lua_runtime._sandbox_run(lua_script, memory_limit=100)

    def test_lua_sandbox_python_isolation(self):
        lua_runtime = LuaRuntime()
        lua_script = '''return python == nil'''
        result = lua_runtime._sandbox_run(lua_script)[0]
        self.assertTrue(result, "Python environment is accessible in Lua sandbox")

    def test_lua_sandbox_protected_environment(self):
        lua_runtime = LuaRuntime()
        lua_script = '''return true'''
        with self.assertRaises(RuntimeExecutionError):
            lua_runtime._sandbox_run(lua_script, {"print": None})

    def test_lua_sandbox_error_catching(self):
        lua_runtime = LuaRuntime()
        lua_script = '''return true'''
        with self.assertRaises(RuntimeExecutionError):
            # Restrict the sandbox so we fail in setup
            lua_runtime._sandbox_run(lua_script, instruction_limit=10, memory_limit=10)

    def test_lua_sandbox_library_whitelist(self):
        lua_runtime = LuaRuntime()
        lua_script = '''require('unwhitelisted_module')'''
        with self.assertRaises(RuntimeSandboxViolationError):
            lua_runtime._sandbox_run(lua_script)

class LuaSandboxLibrariesTestCase(TestCase):
    # Functions that we do not want to expose to our sandbox
    SUPPORTED_LIBRARIES = [
        'cjson',
        'imlib2',
    ]

    @parameterized.expand(SUPPORTED_LIBRARIES)
    def test_lua_sandbox_load_library(self, library):
        lua_runtime = LuaRuntime()
        lua_script = '''require('{}')'''.format(library)
        result = lua_runtime._sandbox_run(lua_script)[0]
        self.assertTrue(result, "Lua library {} can not be loaded in the sandbox".format(library))