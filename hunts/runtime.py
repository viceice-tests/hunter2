from lupa import LuaRuntime

STATIC = 'S'
LUA = 'L'
REGEX = 'R'

RUNTIMES = (
    (STATIC, 'Static Runtime'),
    (LUA, 'Lua Runtime'),
    (REGEX, 'Regex Runtime'),
)

lua = LuaRuntime()
lua_environment_eval = lua.eval("""\
    function (ld, args)
        local sandbox_env = {
            assert = _G.assert,
            bit32 = _G.bit32,
            error = _G.error,
            getmetatable = _G.getmetatable,
            ipairs = _G.ipairs,
            math = _G.math,
            next = _G.next,
            pairs = _G.pairs,
            pcall = _G.pcall,
            print = _G.print,
            rawequal = _G.rawequal,
            rawget = _G.rawget,
            rawlen = _G.rawlen,
            rawset = _G.rawset,
            select = _G.select,
            setmetatable = _G.setmetatable,
            string = _G.string,
            table = _G.table,
            tonumber = _G.tonumber,
            tostring = _G.tostring,
            type = _G.type,
            xpcall = _G.xpcall,
        }
        if args then for k,v in pairs(args) do sandbox_env[k] = v end end
        local chunk = load(ld, ld, "t", sandbox_env)
        local rtrn = chunk()
        return rtrn
    end
""")


def lua_runtime_eval(ld, args={}):
    lua_args = lua.table_from(args)
    return lua_environment_eval(ld, lua_args)


runtime_eval = {
    STATIC: lambda x, *args: x,
    LUA: lua_runtime_eval,
}

runtime_validate = {
    STATIC: lambda validator, args: answer == args['guess'],
    LUA: lambda validator, args: lua_runtime_eval(answer, args),
    REGEX: lambda validator, args: re.fullmatch(answer, args['guess'])
}
