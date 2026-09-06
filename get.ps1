# get.ps1 - one-line install for Windows / PowerShell.
#   irm https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/release/get.ps1 | iex
#   With flags:  $args = @('--pull'); irm <url> | iex
#   Env vars: LUMOS_HOME, LUMOS_URL, LUMOS_BRANCH (default: release; the dev line is main)
#
# ASCII-ONLY, NO BOM. This is not a style preference:
#   - No BOM + non-ASCII: when the file is run from disk, PowerShell 5.1 decodes it with the
#     system ANSI codepage. On CJK systems a DBCS lead byte eats the next byte and breaks
#     quote pairing -> parse error, nothing gets installed.
#   - BOM: `irm | iex` receives a plain string and PowerShell does NOT strip the BOM, so
#     U+FEFF becomes line 1 content and that comment line is executed as a command.
#   Both were hit on a real Windows machine (2026-08-03). ASCII-only removes the whole class.
#   Same rule as slim/*.ps1; see the graph note Systems/slim-get (one-line install) for the full story.
#   Chinese wording for this script lives in that note, not in this file.
#
# This delegates to `lumos bootstrap`, same as get.sh. It used to run `install --force` only,
# which set up the machine layer but not the project layer - so Windows users finished the
# documented "one command does it all" with nothing wired inside their project.
$ErrorActionPreference = "Stop"

function Invoke-LumosGet {
  param([string[]]$ScriptArgs)   # NOT $Args: that is an automatic variable and would be shadowed
  $homeDir = if ($env:LUMOS_HOME) { $env:LUMOS_HOME } else { "$HOME\harness\lumos-toolchain" }
  $url = if ($env:LUMOS_URL) { $env:LUMOS_URL } else { "https://github.com/EnzoHsieh-Android/Lumos" }
  $branch = if ($env:LUMOS_BRANCH) { $env:LUMOS_BRANCH } else { "release" }

  $pass = @()
  foreach ($f in $ScriptArgs) {
    if ($f -eq '--pull' -or $f -eq '--init') { $pass += $f }
    else { Write-Warning "unknown option $f - ignored (only --pull and --init are accepted)" }
  }

  if (-not (Test-Path "$homeDir\scripts\lumos")) {
    New-Item -ItemType Directory -Force -Path (Split-Path $homeDir) | Out-Null
    Write-Host "[clone] cloning Lumos ($branch, the public channel) -> $homeDir ..."
    # Fall back to the default branch: the release branch may not exist yet and a cold
    # start must not die because of that. Branch, not tag: a tag gives a detached HEAD and
    # every later `git pull` / `lumos update` would silently stay on the install-time version.
    git clone --branch $branch $url $homeDir 2>$null
    if ($LASTEXITCODE -ne 0) {
      Write-Warning "cannot reach the '$branch' channel (branch missing or renamed); using the default branch - you are getting the development line."
      git clone $url $homeDir
      if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
    }
  } else {
    Write-Host "[clone] Lumos source already at: $homeDir"
  }

  $env:LUMOS_HOME = $homeDir
  python "$homeDir\scripts\lumos" bootstrap @pass
  if ($LASTEXITCODE -ne 0) { throw "bootstrap failed with exit code $LASTEXITCODE" }

  Write-Host ""
  Write-Host "Done. Last step: restart your Claude Code session (hooks load at session start)."
}

Invoke-LumosGet -ScriptArgs $args
