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

local function trim(str)
    return (str:gsub("^%s+", ""):gsub("%s+$", ""))
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

local function normalize_repo_slug(value)
    if not value then
        return value
    end
    local cleaned = value
    cleaned = cleaned:gsub("^git@[^:]+:", "")
    cleaned = cleaned:gsub("^ssh://[^/]+/", "")
    cleaned = cleaned:gsub("^https?://[^/]+/", "")
    cleaned = cleaned:gsub("^/", "")
    cleaned = cleaned:gsub("%.git$", "")
    return cleaned
end

local function repo_slug_from_remote(url)
    if not url or url == "" then
        return url
    end
    return normalize_repo_slug(trim(url))
end

local function project_from_slug(slug)
    if not slug then
        return slug
    end
    local project = slug:match("([^/]+)$")
    return project
end

local resolved_values = {}

-- Environment variables as used e.g. in GitLab CI.
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
        process_env = function(value, source)
            if source == "GITHUB_SHA" then
                return value:sub(1, 7)
            end
            return value
        end,
    },
    GitLongSHA = {
        env = {
            "CI_COMMIT_SHA",
            "GITHUB_SHA",
        },
        cmd = "git rev-parse HEAD",
    },
    GitRepositorySlug = {
        env = {
            "CI_PROJECT_PATH",
            "CI_REPOSITORY_URL",
            "GITHUB_REPOSITORY",
            "FORGEJO_REPOSITORY",
            "GITEA_REPOSITORY",
            "CI_REPO_OWNER" -- fallback for some runners
        },
        cmd = "git config --get remote.origin.url",
        process_env = function(value, source)
            if source == "CI_REPOSITORY_URL" then
                return repo_slug_from_remote(value)
            end
            return normalize_repo_slug(value)
        end,
        process_cmd = function(value)
            return repo_slug_from_remote(value)
        end,
    },
    GitProjectName = {
        env = {
            "CI_PROJECT_TITLE",
            "CI_PROJECT_NAME",
            "GITHUB_REPOSITORY",
            "FORGEJO_REPOSITORY",
            "GITEA_REPOSITORY",
        },
        cmd = "git config --get remote.origin.url",
        process_env = function(value, source)
            if source == "CI_PROJECT_TITLE" or source == "CI_PROJECT_NAME" then
                return value
            end
            local slug = normalize_repo_slug(value)
            return project_from_slug(slug)
        end,
        process_cmd = function(value)
            return project_from_slug(repo_slug_from_remote(value))
        end,
    },
}

for macro_name, content_sources in pairs(macro_content_sources) do
    -- Default: check for environment variable:
    local cmd = content_sources.cmd
    local content = "n.a."  -- Default value
    local env_content, env_name = first_env_value(content_sources.env)

    if env_content and env_content ~= "" then  -- Empty string evaluates to true
        texio.write_nl("Found and will be using environment variable '"..env_name.."'.")
        if content_sources.process_env then
            local ok, processed = pcall(content_sources.process_env, env_content, env_name)
            if ok and processed and processed ~= "" then
                content = processed
            else
                content = env_content
            end
        else
            content = env_content
        end
    else
        local env_names = content_sources.env
        if type(env_names) == "table" then
            env_names = table.concat(env_names, ", ")
        end
        env_names = env_names or "(none)"
        texio.write_nl("Environment variable(s) '"..env_names.."' undefined or empty, trying fallback command.")
        -- luatex reference for shell escape:
        -- "0 means disabled, 1 means anything is permitted, and 2 is restricted"
        if status.shell_escape == 1 then
            local cmd_success, cmd_stdout = pcall(get_cmd_stdout, cmd)
            if cmd_success then
                texio.write_nl("Fallback command '"..cmd.."' succeeded.")
                local processed = cmd_stdout
                if content_sources.process_cmd then
                    local ok, result = pcall(content_sources.process_cmd, cmd_stdout)
                    if ok and result and result ~= "" then
                        processed = result
                    end
                end
                content = processed
            else
                texio.write_nl("Fallback command '"..cmd.."' unsuccessful.")
            end
        else
            texio.write_nl("shell-escape is disabled, cannot use fallback command.")
        end
    end

    -- Shouldn't happen, would be programmer error, therefore assert Python-style
    assert(content, "Content not defined (neither success nor fallback present)")
    content = trim(content)

    --[[
        The `content` can contain unprintable characters, like underscores in git branch
        names. Towards this end, use detokenize in the macro itself, which will make all
        characters printable (assigns category code 12). See also:
        https://www.overleaf.com/learn/latex/Articles/An_Introduction_to_LuaTeX_(Part_2):_Understanding_%5Cdirectlua
    --]]
    local escaped_content = "\\detokenize{"..content.."}"

    texio.write_nl("Providing new macro '"..macro_name.."' with contents: '"..escaped_content.."'.")
    --  Set a macro (`\newcommand`) see also: https://tex.stackexchange.com/a/450892/120853
    token.set_macro(macro_name, escaped_content)
    resolved_values[macro_name] = content
end

if (not resolved_values.GitProjectName or resolved_values.GitProjectName == "" or resolved_values.GitProjectName == "n.a.") and resolved_values.GitRepositorySlug and resolved_values.GitRepositorySlug ~= "" and resolved_values.GitRepositorySlug ~= "n.a." then
    local project = project_from_slug(resolved_values.GitRepositorySlug)
    if project and project ~= "" then
        local escaped = "\\detokenize{"..project.."}"
        texio.write_nl("Deriving GitProjectName from GitRepositorySlug.")
        token.set_macro("GitProjectName", escaped)
        resolved_values.GitProjectName = project
    end
end

do
    local base_url_env, _ = first_env_value({
        "OMNILATEX_VERIFICATION_BASE_URL",
        "VERIFICATION_BASE_URL",
        "CF_PAGES_URL",
        "PAGES_URL",
        "DEPLOYMENT_URL",
        "PAGES_BASE_URL"
    })
    if base_url_env and base_url_env ~= "" then
        local cleaned = trim(base_url_env)
        cleaned = cleaned:gsub("/$", "")
        local escaped = "\\detokenize{"..cleaned.."}"
        texio.write_nl("Setting macro 'GitHostPagesURL' from environment.")
        token.set_macro("GitHostPagesURL", escaped)
        token.set_macro("GITHOST_PAGES_URL", escaped)
    end
end
