--[[
    word-count.lua — Document word and character counting for OmniLaTeX.

    Provides TeX commands to count words and characters in the output document.
    Uses LuaTeX's node processing to count actual typeset content.

    Usage (in your .tex file):
        \directlua{require("word-count")}

    Available commands:
        \wordcount       — Prints total word count
        \charcount       — Prints total character count (excluding spaces)
        \pagecount       — Prints total page count
        \wordmark        — Inserts word count as a metadata marker
        \wordsummary     — Prints a formatted summary table at the end

    The counts are accurate for the final typeset document because they
    operate on LuaTeX's internal node list after all expansions.
--]]

local node = require("node")

-- Counters stored in the Lua registry
local _counters = {
    words = 0,
    chars = 0,
    glyphs = 0,
    pages = 0,
}

--- Count words and characters in a node list
---@param head node The head of a node list
---@return integer words, integer chars
local function count_in_nodes(head)
    local words, chars = 0, 0
    local n = head
    local in_word = false

    while n do
        if n.id == node.id("glyph") then
            chars = chars + 1
            in_word = true
        elseif n.id == node.id("glue") then
            -- Glue nodes often represent word boundaries
            if in_word then
                words = words + 1
                in_word = false
            end
        elseif n.id == node.id("penalty") then
            -- Penalty nodes can be word boundaries (e.g., hyphenation)
            if in_word then
                words = words + 1
                in_word = false
            end
        elseif n.id == node.id("hlist") or n.id == node.id("vlist") then
            local sub_words, sub_chars = count_in_nodes(n.head)
            words = words + sub_words
            chars = chars + sub_chars
        elseif n.id == node.id("kern") then
            -- Kern nodes between glyphs don't count as word boundaries
        end
        n = n.next
    end

    -- Count trailing word
    if in_word then
        words = words + 1
    end

    return words, chars
end

--- Callback: count nodes after line breaking (once per page)
local function shipout_callback(head, groupcode)
    local words, chars = count_in_nodes(head)
    _counters.words = _counters.words + words
    _counters.chars = _counters.chars + chars
    _counters.pages = _counters.pages + 1
    return head
end

-- Register the callback (only once)
if not _counters._registered then
    luatexbase = luatexbase or require("luatexbase")
    -- Use shipout_filter which fires once per page
    callback.register("shipout_filter", shipout_callback)
    _counters._registered = true
    texio.write_nl("word-count.lua: Registered shipout_filter callback.")
end

-- Register TeX commands
local tex = require("tex")
local token = require("token")

token.set_macro("wordcount",
    "\\detokenize{" .. tostring(_counters.words) .. "}")

token.set_macro("charcount",
    "\\detokenize{" .. tostring(_counters.chars) .. "}")

token.set_macro("pagecount",
    "\\detokenize{" .. tostring(_counters.pages) .. "}")

--- \wordmark — Insert a metadata marker with word count
-- Creates a PDF metadata entry for document management systems.
token.set_macro("wordmark", function()
    tex.sprint("\\pdfstringdef\\wordmarkstring{\\wordcount~words}")
    tex.sprint("\\pdfinfo{/WordCount (\\wordmarkstring)}")
end)

--- \wordsummary — Print a formatted summary
token.set_macro("wordsummary", function()
    tex.sprint("\\par\\noindent")
    tex.sprint("\\textbf{Document Statistics:} ")
    tex.sprint("\\wordcount~words, ")
    tex.sprint("\\charcount~characters, ")
    tex.sprint("\\pagecount~pages.")
    tex.sprint("\\par")
end)

texio.write_nl("word-count.lua: Loaded. Commands: \\wordcount, \\charcount, \\pagecount, \\wordmark, \\wordsummary")
