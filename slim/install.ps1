# install.ps1 — 薄殼:所有安裝邏輯已搬進 install.py(stdlib only,Unix/Windows
# 共用同一份原始碼)。本檔案只做兩件事:①定位套件目錄(自己所在目錄)②挑一支
# 可用的 python 直譯器,把參數原樣轉發給 install.py。
#
# 形態沿用本 repo 完整版 `get.ps1` 的先例(幾乎什麼都不做,把工作丟給 python)。
#
# ★誠實聲明★:這支腳本沒有在真機 Windows 上跑過(開發環境是 macOS,沒有
# PowerShell)——邏輯與 install.sh/install.py 對照移植而來,只驗證過
# install.py 本體透過 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 在非 Windows 機器上跑
# 出的分支邏輯(見 install.py 模組 docstring),這支 .ps1 薄殼本身、Windows
# PATH 的實際行為、`.cmd` shim 在真實 cmd.exe/PowerShell 下能不能被找到,都
# 沒有真機驗證過。
$ErrorActionPreference = "Stop"

$Pkg = Split-Path -Parent $MyInvocation.MyCommand.Path

$Py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $Py) { $Py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Py) {
  Write-Error "ERROR: 找不到 python3 或 python 指令——請先安裝 Python 3 再重跑本腳本。"
  exit 2
}

& $Py.Source "$Pkg\install.py" @args
exit $LASTEXITCODE
