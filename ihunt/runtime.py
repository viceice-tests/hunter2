from lupa import LuaRuntime

STATIC = 'S'
LUA = 'L'

RUNTIMES = (
    (STATIC, 'Static Runtime'),
    (LUA, 'Lua Runtime'),
)

lua = LuaRuntime()
lua_environment_eval = lua.eval("""\
    function (ld, args)
        local sandbox_env = { math = _G.math, print = _G.print, string = _G.string }
        if args then for k,v in pairs(args) do sandbox_env[k] = v end end
        local chunk = load(ld, ld, "t", sandbox_env)
        local rtrn = chunk()
        return rtrn
    end
""")


def lua_runtime_eval(ld, args = {}):
    lua_args = lua.table_from(args)
    return lua_environment_eval(ld, lua_args)


runtime_eval = {
    STATIC: lambda x, *args: x,
    LUA: lua_runtime_eval,
}
