--[[
    todo-tracker.lua — Collect and report TODO items in LaTeX documents.

    Scans the TeX input buffer for \todo{...} commands and collects them.
    At the end of the document, prints a summary of all TODOs found.

    Usage (in your .tex file):
        \directlua{require("todo-tracker")}

    In your document:
        \todo{Fix the bibliography formatting}
        \todo[high]{Add missing figures for Chapter 3}
        \todo[low]{Consider rewriting the introduction}

    At the end (or anywhere):
        \todolist   — Print all collected TODOs grouped by priority

    The tracker supports priority levels:
        - high   (or critical, important)
        - medium (or normal, default)
        - low    (or minor, optional)

    If no priority is specified, defaults to "medium".
--]]

local _todos = {}
local _todo_counter = 0

--- Parse priority from the optional argument
---@param arg string|nil The optional argument string
---@return string priority
local function parse_priority(arg)
    if not arg or arg == "" then
        return "medium"
    end
    local lower = arg:lower()
    if lower == "high" or lower == "critical" or lower == "important" then
        return "high"
    elseif lower == "low" or lower == "minor" or lower == "optional" then
        return "low"
    end
    return "medium"
end

--- Process the TeX input buffer for \todo commands
local function process_input_buffer(buffer)
    -- Match \todo[optional]{text} and \todo{text}
    local pattern = "\\todo%[([^%]]*)%]{([^}]*)}"
    local simple_pattern = "\\todo{([^}]*)}"

    -- First try with optional argument
    for arg, text in buffer:gmatch(pattern) do
        _todo_counter = _todo_counter + 1
        table.insert(_todos, {
            id = _todo_counter,
            text = text,
            priority = parse_priority(arg),
        })
    end

    -- Then try without optional argument (if the above didn't match)
    if _todo_counter == 0 then
        for text in buffer:gmatch(simple_pattern) do
            _todo_counter = _todo_counter + 1
            table.insert(_todos, {
                id = _todo_counter,
                text = text,
                priority = "medium",
            })
        end
    end

    return buffer
end

--- Get todos grouped by priority
---@return table grouped
local function group_by_priority()
    local grouped = { high = {}, medium = {}, low = {} }
    for _, todo in ipairs(_todos) do
        table.insert(grouped[todo.priority], todo)
    end
    return grouped
end

-- Register the input buffer callback (only once)
if not _todos._registered then
    callback.register("process_input_buffer", process_input_buffer)
    _todos._registered = true
    texio.write_nl("todo-tracker.lua: Registered process_input_buffer callback.")
end

-- Register TeX commands
local tex = require("tex")

--- \todolist — Print formatted summary of all TODOs
tex.sprint = tex.sprint or function(...) -- ensure tex.sprint exists
    -- Fallback: just use tex.print
end

-- Use a simpler approach: define the todolist command via token
local token = require("token")

token.set_macro("todocount",
    "\\detokenize{" .. tostring(#_todos) .. "}")

-- For \todolist, we need a more complex approach since it
-- requires iterating at expansion time. We use a Lua function.
local function cmd_todolist()
    if #_todos == 0 then
        tex.sprint("\\noindent\\textit{No TODOs found.}")
        return
    end

    local grouped = group_by_priority()

    tex.sprint("\\par\\bigskip")
    tex.sprint("\\noindent\\textbf{TODO Summary: " .. #_todos .. " item(s)}")
    tex.sprint("\\par\\medskip")

    -- High priority
    if #grouped.high > 0 then
        tex.sprint("\\textcolor{red}{\\textbf{High Priority (" .. #grouped.high .. ")}}")
        tex.sprint("\\begin{itemize}")
        for _, todo in ipairs(grouped.high) do
            tex.sprint("\\item " .. todo.text .. " \\hfill\\texttt{[TODO-" .. todo.id .. "]}")
        end
        tex.sprint("\\end{itemize}")
    end

    -- Medium priority
    if #grouped.medium > 0 then
        tex.sprint("\\textcolor{orange}{\\textbf{Medium Priority (" .. #grouped.medium .. ")}}")
        tex.sprint("\\begin{itemize}")
        for _, todo in ipairs(grouped.medium) do
            tex.sprint("\\item " .. todo.text .. " \\hfill\\texttt{[TODO-" .. todo.id .. "]}")
        end
        tex.sprint("\\end{itemize}")
    end

    -- Low priority
    if #grouped.low > 0 then
        tex.sprint("\\textcolor{gray}{\\textbf{Low Priority (" .. #grouped.low .. ")}}")
        tex.sprint("\\begin{itemize}")
        for _, todo in ipairs(grouped.low) do
            tex.sprint("\\item " .. todo.text .. " \\hfill\\texttt{[TODO-" .. todo.id .. "]}")
        end
        tex.sprint("\\end{itemize}")
    end
end

-- Register as a TeX command
-- Using luatexbase if available, otherwise direct registration
local ok, luatexbase = pcall(require, "luatexbase")
if ok then
    luatexbase.new_command("todolist", {}, cmd_todolist)
else
    -- Fallback: register via token
    token.set_macro("todolist", function()
        cmd_todolist()
    end)
end

texio.write_nl("todo-tracker.lua: Loaded. Commands: \\todo{text}, \\todo[priority]{text}, \\todolist")
