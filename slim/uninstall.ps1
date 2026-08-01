# uninstall.ps1 — 薄殼:所有卸載邏輯已搬進 uninstall.py(stdlib only,Unix/
# Windows 共用同一份原始碼)。本檔案只做兩件事:①定位套件目錄(自己所在目錄)
# ②挑一支可用的 python 直譯器,把參數原樣轉發給 uninstall.py。
#
# ★誠實聲明★(與 install.ps1 同款):沒有在真機 Windows 上跑過,只有 uninstall.py
# 本體透過 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 驗過分支邏輯。
#
# ★2026-08 Task 14 修復③(保險性修法,★這段語意本身也沒有真機驗證過★,與
# install.ps1 同款理由,細節見該檔案同一段註解)★:收尾不再呼叫裸的 `exit`
# (避免在 `& "路徑\uninstall.ps1"` 這種呼叫鏈裡把呼叫端整個 session 關掉),
# 改把子行程 rc 寫回 `$LASTEXITCODE` 供呼叫端讀取。
$ErrorActionPreference = "Stop"

$Pkg = Split-Path -Parent $MyInvocation.MyCommand.Path

$Py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $Py) { $Py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Py) {
  Write-Error "ERROR: 找不到 python3 或 python 指令——請先安裝 Python 3 再重跑本腳本。"
  exit 2
}

& $Py.Source "$Pkg\uninstall.py" @args
$global:LASTEXITCODE = $LASTEXITCODE
