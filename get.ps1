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
#   Same rule as slim/*.ps1; the Chinese write-up lives in the graph note, not in this file.
#
# This delegates to `lumos bootstrap`, same as get.sh. It used to run `install --force` only,
# which set up the machine layer but not the project layer - so Windows users finished the
# documented "one command does it all" with nothing wired inside their project.

function Invoke-LumosGet {
  # NOTE: the parameter must NOT be named $Args. $Args is a PowerShell automatic variable
  # (the function's own unbound arguments) and shadows anything passed in, so every flag
  # would be silently dropped. Same trap as slim/get.ps1.
  param([string[]]$ScriptArgs)

  $ErrorActionPreference = "Stop"

  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "ERROR: git not found. Install git first, then re-run: https://git-scm.com/download/win" -ErrorAction Continue
    return 2
  }

  # Pick the interpreter at run time instead of hardcoding `python`. Machines that only have
  # python3.exe (some official installers, Microsoft Store builds) would otherwise fail right
  # here - before ever reaching the shim fix in `lumos install` that exists for exactly them.
  $py = $null
  foreach ($cand in @('python3', 'python')) {
    if (Get-Command $cand -ErrorAction SilentlyContinue) { $py = $cand; break }
  }
  if (-not $py) {
    Write-Error "ERROR: neither python3 nor python found on PATH. Install Python 3.9+ and re-run." -ErrorAction Continue
    return 2
  }

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
    # later `git pull` / `lumos update` then refuse to move (they fail closed and say so).
    git clone --branch $branch $url $homeDir 2>$null
    # $ErrorActionPreference = "Stop" does NOT cover native executables: git.exe returning
    # non-zero does not terminate. Check $LASTEXITCODE explicitly. (Same note as slim/get.ps1.)
    if ($LASTEXITCODE -ne 0) {
      Write-Warning "cannot reach the '$branch' channel (branch missing or renamed); using the default branch - you are getting the development line."
      git clone $url $homeDir
      if ($LASTEXITCODE -ne 0) {
        Write-Error "ERROR: clone of $url failed (check your network and access to that repo)." -ErrorAction Continue
        return 2
      }
    }
  } else {
    Write-Host "[clone] Lumos source already at: $homeDir"
  }

  $env:LUMOS_HOME = $homeDir
  # `| Out-Host` is required: a function's `return` also emits every unconsumed output,
  # so without it the caller receives Object[] instead of Int32. (Same note as slim/get.ps1.)
  & $py "$homeDir\scripts\lumos" bootstrap @pass | Out-Host
  if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: bootstrap failed with exit code $LASTEXITCODE." -ErrorAction Continue
    return $LASTEXITCODE
  }

  Write-Host ""
  Write-Host "Done. Last step: restart your Claude Code session (hooks load at session start)."
  return 0
}

$rc = Invoke-LumosGet -ScriptArgs $args
$global:LASTEXITCODE = $rc
