--[[
    conditional-include.lua — Conditional section inclusion for OmniLaTeX.

    Allows including or excluding sections of a document based on flags.
    Useful for:
      - Draft vs. final versions (hide draft notes, show TODOs)
      - Instructor vs. student versions (hide solutions)
      - Short vs. long versions (include/exclude appendices)

    Usage (in your .tex file):
        \directlua{require("conditional-include")}

    Then define flags:
        \setflag{draft}           — Enable the "draft" flag
        \setflag{solutions}       — Enable the "solutions" flag
        \clearflag{draft}         — Disable the "draft" flag

    Use conditional blocks:
        \begin{onlyif}{draft}
          This text only appears when the "draft" flag is set.
        \end{onlyif}

        \begin{unless}{draft}
          This text appears when the "draft" flag is NOT set.
        \end{unless}

        \begin{onlyif}{solutions}
          The answer is 42.
        \end{onlyif}

    You can also check flags from the command line:
        lualatex '\directlua{require("conditional-include")}\\setflag{solutions}\input{main}'

    Or via environment variables:
        LATEX_FLAGS=draft,solutions lualatex main.tex

    This script also reads the LATEX_FLAGS environment variable on load,
    automatically enabling any comma-separated flags it contains.
--]]

local _flags = {}

--- Set a flag
---@param name string The flag name
local function set_flag(name)
    name = name:match("^%s*(.-)%s*$")  -- trim whitespace
    if name and name ~= "" then
        _flags[name] = true
    end
end

--- Clear a flag
---@param name string The flag name
local function clear_flag(name)
    name = name:match("^%s*(.-)%s*$")  -- trim whitespace
    if name and name ~= "" then
        _flags[name] = nil
    end
end

--- Check if a flag is set
---@param name string The flag name
---@return boolean
local function has_flag(name)
    name = name:match("^%s*(.-)%s*$")  -- trim whitespace
    return _flags[name] == true
end

--- Read flags from environment variable on load
local env_flags = os.getenv("LATEX_FLAGS")
if env_flags and env_flags ~= "" then
    for flag in env_flags:gmatch("[^,]+") do
        set_flag(flag)
        texio.write_nl("conditional-include.lua: Enabled flag from LATEX_FLAGS: " .. flag)
    end
end

-- Register TeX commands
local tex = require("tex")
local token = require("token")

--- \setflag{name} — Set a flag
token.set_macro("setflag", function(name)
    -- name is already detokenized by TeX
    set_flag(name)
end)

--- \clearflag{name} — Clear a flag
token.set_macro("clearflag", function(name)
    clear_flag(name)
end)

--- \ifflag{name}{true}{false} — Conditional expansion
-- Usage: \ifflag{draft}{Draft text}{Final text}
local function cmd_ifflag(name, true_text, false_text)
    if has_flag(name) then
        tex.sprint(true_text)
    else
        tex.sprint(false_text)
    end
end

-- Register \ifflag using luatexbase or fallback
local ok, luatexbase = pcall(require, "luatexbase")
if ok then
    luatexbase.new_command("ifflag", {
        { "name" }, { "true_text" }, { "false_text" }
    }, cmd_ifflag)
else
    token.set_macro("ifflag", function()
        -- Fallback: simpler version
        tex.sprint("[ifflag requires luatexbase]")
    end)
end

--- \begin{onlyif}{flag} ... \end{onlyif}
--- \begin{unless}{flag} ... \end{unless}
--
-- We implement these by hooking into the LaTeX environment system.
-- The environments consume their body and conditionally typeset it.

-- Define \onlyif and \unless as LaTeX environments
-- This is done via \newenvironment in LaTeX, triggered from Lua.

local function setup_environments()
    tex.sprint("\\newenvironment{onlyif}[1]{")
    tex.sprint("  \\ifflag{#1}{}")
    tex.sprint("  \\def\\endonlyif{")
    tex.sprint("  }")
    tex.sprint("}{")
    tex.sprint("  \\endonlyif")
    tex.sprint("}")

    tex.sprint("\\newenvironment{unless}[1]{")
    tex.sprint("  \\ifflag{#1}")
    tex.sprint("    \\def\\endunless{")
    tex.sprint("      \\endunless")
    tex.sprint("    }")
    tex.sprint("  }")
    tex.sprint("}{")
    tex.sprint("  \\endunless")
    tex.sprint("}")
end

-- Defer environment setup to \AtBeginDocument so packages are loaded
local function at_begin_document()
    setup_environments()
end

-- Register via callback
local function finish_callback()
    setup_environments()
end

if not _flags._registered then
    callback.register("finish_pdffile", finish_callback)
    _flags._registered = true
end

--- \flaglist — Print all active flags (useful for debugging)
local function cmd_flaglist()
    local flag_names = {}
    for name, _ in pairs(_flags) do
        if name ~= "_registered" then
            table.insert(flag_names, name)
        end
    end
    table.sort(flag_names)

    if #flag_names == 0 then
        tex.sprint("\\noindent\\textit{No flags set.}")
    else
        tex.sprint("\\noindent\\textbf{Active flags:} ")
        tex.sprint(table.concat(flag_names, ", "))
    end
end

local ok2, luatexbase2 = pcall(require, "luatexbase")
if ok2 then
    luatexbase.new_command("flaglist", {}, cmd_flaglist)
else
    token.set_macro("flaglist", function()
        cmd_flaglist()
    end)
end

texio.write_nl("conditional-include.lua: Loaded. Commands: \\setflag{name}, \\clearflag{name}, \\ifflag{name}{true}{false}, \\flaglist")
texio.write_nl("conditional-include.lua: Environments: onlyif, unless. Env var: LATEX_FLAGS=flag1,flag2")
