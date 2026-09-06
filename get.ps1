# get.ps1 — 用法:  irm https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/release/get.ps1 | iex
#   帶旗標(--pull / --init):
#     $args = @('--pull'); irm <url> | iex
#   環境變數:LUMOS_HOME、LUMOS_URL、LUMOS_BRANCH(預設 release;開發線是 main)
#
# ★這支跟 get.sh 做同一件事,所以也整段委派 bootstrap★(2026-09-07 #7):
# 之前它只跑 install --force,少了 bootstrap 的專案層接線,於是 Windows 使用者裝完
# 只有機器層、專案裡什麼都沒有,而文件寫的是「一次到位」。兩邊行為不一致比少功能更糟。
$ErrorActionPreference = "Stop"

function Invoke-LumosGet {
  param([string[]]$Flags)
  $homeDir = if ($env:LUMOS_HOME) { $env:LUMOS_HOME } else { "$HOME\harness\lumos-toolchain" }
  $url = if ($env:LUMOS_URL) { $env:LUMOS_URL } else { "https://github.com/EnzoHsieh-Android/Lumos" }
  $branch = if ($env:LUMOS_BRANCH) { $env:LUMOS_BRANCH } else { "release" }

  # 只認 get.sh 認得的那兩個旗標,其餘出提醒後略過(兩支的行為要一樣)
  $pass = @()
  foreach ($f in $Flags) {
    if ($f -eq '--pull' -or $f -eq '--init') { $pass += $f }
    else { Write-Warning "不認得 $f 這個選項,略過(只認 --pull 和 --init)" }
  }

  if (-not (Test-Path "$homeDir\scripts\lumos")) {
    New-Item -ItemType Directory -Force -Path (Split-Path $homeDir) | Out-Null
    Write-Host "[clone] clone Lumos($branch 對外線)→ $homeDir …"
    # 對外線抓不到就退回預設分支:release 分支可能還沒開,冷啟動不該因此炸掉
    git clone --branch $branch $url $homeDir 2>$null
    if ($LASTEXITCODE -ne 0) {
      Write-Warning "抓不到 $branch 這條對外線(分支還沒開、或名字改了),改用預設分支;你拿到的是開發線的內容。"
      git clone $url $homeDir
      if ($LASTEXITCODE -ne 0) { throw "git clone 失敗" }
    }
  } else {
    Write-Host "[clone] Lumos 源已在: $homeDir"
  }

  $env:LUMOS_HOME = $homeDir
  python "$homeDir\scripts\lumos" bootstrap @pass
  if ($LASTEXITCODE -ne 0) { throw "bootstrap 失敗,回傳碼 $LASTEXITCODE" }

  Write-Host "`n✓ 完成。最後一步:**重啟 Claude Code session**(hooks 在 session start 載入)"
}

Invoke-LumosGet -Flags $args
