--[[
    The following import is not required since in LuaTeX's `\directlua` environment,
    `token` etc. is already available. However, this is nice to keep linters from
    complaining about an undefined variable.
--]]
local token = require("token")
local texio = require("texio")
local status = require("status")

--[[
    Trying to incorporate dynamic values into certain newcommand macros. Their
    contents are set at build-time according to environment variables. This is useful
    for automatic workflows in CI environments. See also:
    https://tex.stackexchange.com/a/1739/120853.
    An alternative to using environment variables are command line arguments:
    https://tex.stackexchange.com/a/18813/120853
    However, this seems more error-prone and requires more steps, e.g. piping arguments
    to `lualatex` through `latexmk` first, etc.
    The previous approach was to `sed` for certain `newcommand` definitions in an
    additional CI job. This was much more error-prone (bash scripting) and less
    easily expanded than the below approach.
    LuaTeX provides excellent access to TeX, making this implementation much easier.
--]]

local function get_cmd_stdout(cmd)
    -- See: https://stackoverflow.com/a/326715/11477374
    local fh = assert(io.popen(cmd))
    local first_line = assert(fh:read())
    fh:close()
    return first_line
end

local function first_env_value(env_spec)
    if not env_spec then
        return nil, nil
    end
    if type(env_spec) == "string" then
        env_spec = { env_spec }
    end
    for _, name in ipairs(env_spec) do
        local value = os.getenv(name)
        if value and value ~= "" then
            return value, name
        end
    end
    return nil, nil
end

local function normalize_ref(ref)
    if not ref then
        return ref
    end
    local cleaned = ref:gsub("^refs/heads/", "")
    cleaned = cleaned:gsub("^refs/tags/", "")
    cleaned = cleaned:gsub("^refs/remotes/", "")
    return cleaned
end

local function shorten_sha(sha)
    if not sha or #sha < 7 then
        return sha
    end
    return sha:sub(1, 7)
end

-- Environment variables as used e.g. in GitLab CI, GitHub Actions, etc.
-- Otherwise, e.g. when developing locally, use commands as a fallback.
local macro_content_sources = {
    GitRefName = {
        env = {
            "CI_COMMIT_REF_NAME",
            "GITHUB_REF_NAME",
            "GITHUB_HEAD_REF",
            "GITHUB_REF",
        },
        cmd = "git rev-parse --abbrev-ref HEAD",
        process_env = function(value)
            return normalize_ref(value)
        end,
    },
    GitShortSHA = {
        env = {
            "CI_COMMIT_SHORT_SHA",
            "GITHUB_SHA",
        },
        cmd = "git rev-parse --short HEAD",
        process_env = function(value)
            return shorten_sha(value)
        end,
        process_cmd = function(value)
            return shorten_sha(value)
        end,
    },
    GitLongSHA = {
        env = {
            "CI_COMMIT_SHA",
            "GITHUB_SHA",
        },
        cmd = "git rev-parse HEAD",
        allow_empty = true,
    },
    GitHostPagesURL = {
        env = {
            "GITHUB_PAGES_URL",
            "GITHUB_REPOSITORY",
        },
        cmd = "git remote get-url origin",
        process_env = function(value, name)
            if name == "GITHUB_PAGES_URL" then
                return value
            elseif name == "GITHUB_REPOSITORY" then
                local user, repo = value:match("([^/]+)/(.+)")
                if user and repo then
                    return "https://" .. user .. ".github.io/" .. repo
                end
            end
            return nil
        end,
        process_cmd = function(url)
            local user, repo = url:match("github%.com[:/]([^/]+)/([^/]+)")
            if user and repo then
                repo = repo:gsub("%.git$", "")
                return "https://" .. user .. ".github.io/" .. repo
            end
            return nil
        end,
        allow_empty = false,
    },
}

for macro_name, content_sources in pairs(macro_content_sources) do
    local content = nil
    local source = nil

    -- First, try environment variables
    local env_content, env_name = first_env_value(content_sources.env)
    if env_content then
        texio.write_nl("Found environment variable '" .. env_name .. "' for " .. macro_name .. ".")
        content = env_content
        source = "env"
        if content_sources.process_env then
            content = content_sources.process_env(content)
        end
    else
        local env_names = content_sources.env
        if type(env_names) == "table" then
            env_names = table.concat(env_names, ", ")
        end
        texio.write_nl("No environment variable found for " .. macro_name .. " (checked: " .. env_names .. "). Trying Git command fallback.")
    end

    -- If no env, try Git command if shell escape enabled
    if not content and status.shell_escape == 1 then
        local cmd_success, cmd_stdout = pcall(get_cmd_stdout, content_sources.cmd)
        if cmd_success and cmd_stdout then
            texio.write_nl("Git command '" .. content_sources.cmd .. "' succeeded for " .. macro_name .. ".")
            content = cmd_stdout
            source = "cmd"
            if content_sources.process_cmd then
                content = content_sources.process_cmd(content)
            end
        else
            texio.write_nl("Git command '" .. content_sources.cmd .. "' failed for " .. macro_name .. ".")
        end
    elseif not content then
        texio.write_nl("Shell escape disabled, cannot use Git command fallback for " .. macro_name .. ".")
    end

    -- If still no content, log failure and set to empty (unless allow_empty is false)
    if not content then
        if content_sources.allow_empty == false then
            texio.write_nl("Failed to retrieve " .. macro_name .. " from environment or Git command. Leaving macro undefined.")
            -- Do not set the macro, allowing fallback in config/document-settings.sty
        else
            texio.write_nl("Failed to retrieve " .. macro_name .. " from environment or Git command. Setting macro to empty.")
            content = ""
        end
    end

    -- Ensure content is a string
    content = tostring(content):gsub("%s+$", "")  -- trim trailing whitespace

    --[[
        The `content` can contain unprintable characters, like underscores in git branch
        names. Towards this end, use detokenize in the macro itself, which will make all
        characters printable (assigns category code 12). See also:
        https://www.overleaf.com/learn/latex/Articles/An_Introduction_to_LuaTeX_(Part_2):_Understanding_%5Cdirectlua
    --]]
    local escaped_content = "\\detokenize{" .. content .. "}"

    if content then
        texio.write_nl("Setting macro '" .. macro_name .. "' to: '" .. escaped_content .. "'.")
        -- Set a macro (`\newcommand`) see also: https://tex.stackexchange.com/a/450892/120853
        token.set_macro(macro_name, escaped_content)
    end
end
