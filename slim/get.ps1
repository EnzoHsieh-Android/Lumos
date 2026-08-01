# get.ps1 — 公開精簡版 一行安裝入口(Windows/PowerShell)
#
# 用法:
#   irm https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/get.ps1 | iex
#
# 邏輯與 get.sh 對稱(逐步翻譯,不是重新設計):
#   ① 把交付包 clone(首次)或更新(已存在時 git pull)到固定落點 ~\.lumos-slim
#   ② 執行套件內的 install.ps1(它只轉發給 install.py,細節見該檔案開頭註解)
#
# ★為什麼要固定落點★:跟 get.sh 同款理由——`irm ... | iex` 執行時沒有穩定的
# 檔案位置可定位自己,且使用者若把套件搬走/刪掉,全域指令就斷了。固定落點也讓
# uninstall.py 有地方可以拿真值(sha256 比對)判斷 `~\.local\bin\lumos` 是不是
# 我們裝的那份(見 install.py 的身分證 manifest 說明——manifest 是主要比對來源,
# 這個固定落點只是找不到 manifest 時的備援)。
#
# ★冪等★:~\.lumos-slim 已存在且是合法 git repo → git pull 更新,不重新 clone。
# 已存在但不像我們的東西(沒有 .git)→ 拒絕動它、印清楚訊息,不猜測、不覆寫。
#
# ★誠實聲明★:沒有在真機 Windows 上跑過(開發環境是 macOS,沒有 PowerShell/
# git-for-Windows 可用)——邏輯照 get.sh 逐步翻譯,git clone/pull 的參數與
# get.sh 相同,但這支腳本本身、`irm | iex` 這種執行方式在真實 Windows 上的行為
# 都沒有真機驗證過。
$ErrorActionPreference = "Stop"

$RepoUrl = if ($env:LUMOS_SLIM_REPO_URL) { $env:LUMOS_SLIM_REPO_URL } else { "https://github.com/citrus-android-developer/Citrus_Lumos.git" }
$Dest = Join-Path $HOME ".lumos-slim"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "ERROR: 找不到 git 指令——請先安裝 git 再重跑這支腳本(https://git-scm.com/download/win)。"
  exit 2
}

if (Test-Path (Join-Path $Dest ".git")) {
  Write-Host "已存在 $Dest,更新到最新版..."
  git -C $Dest pull --ff-only -q
  if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: $Dest 更新失敗(可能有本地改動,或不是 fast-forward)。若你動過裡面的檔案,確認沒有要留的東西後備份/刪掉 $Dest 再重跑本腳本。"
    exit 2
  }
} elseif (Test-Path $Dest) {
  Write-Error "ERROR: $Dest 已存在,但不是本包的 git clone(找不到 $Dest\.git)。為避免誤刪你自己的東西,不會自動覆寫——請自行確認該目錄內容後處理。"
  exit 2
} else {
  Write-Host "首次安裝,clone 到 $Dest..."
  git clone -q $RepoUrl $Dest
}

$InstallScript = Join-Path $Dest "install.ps1"
if (-not (Test-Path $InstallScript)) {
  Write-Error "ERROR: $InstallScript 不存在——交付包內容可能不完整。"
  exit 2
}

& $InstallScript @args
exit $LASTEXITCODE
