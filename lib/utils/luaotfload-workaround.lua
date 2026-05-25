-- Workaround for luaotfload-multiscript.lua crash in Nix/TL2025
-- luaotfload-multiscript calls kpse.find_file("ScriptExtensions.txt")
-- which returns nil, then calls os.exit(-1).
-- Patch kpse.find_file to return a dummy temp file when the real file is missing.

local _orig_find = kpse.find_file
local _tmp_files = {}

kpse.find_file = function(name, ...)
  if name == "ScriptExtensions.txt" then
    local r = _orig_find(name, ...)
    if r then return r end
    local tmp = os.tmpname()
    local fh = io.open(tmp, "w")
    if fh then
      fh:write("# Dummy ScriptExtensions.txt for luaotfload compatibility\n")
      fh:close()
    end
    table.insert(_tmp_files, tmp)
    return tmp
  end
  return _orig_find(name, ...)
end

local ok, luatexbase = pcall(require, "luatexbase")
if ok then
  luatexbase.add_to_callback("finish_run", function()
    for _, f in ipairs(_tmp_files) do
      os.remove(f)
    end
  end, "luaotfload-workaround cleanup")
end
