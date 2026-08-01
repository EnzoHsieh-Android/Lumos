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
#
# ★2026-08 Task 14 修復③(保險性修法,★這段語意本身也沒有真機驗證過★)★:
# 舊版收尾是裸的 `exit $LASTEXITCODE`——PowerShell 的 `exit` 在 README 教的
# 兩種呼叫方式(`irm ... | iex` 一行版、`& "路徑\install.ps1"` 兩行版)下都會
# 終止整個呼叫端 session,不像 bash 子行程只結束自己:使用者貼上指令、安裝其實
# 成功了,但畫面印完「裝好了」之後整個 PowerShell 視窗突然關閉,會被誤以為是
# 崩潰。改成不呼叫 `exit`,只把子行程(`install.py`)的 rc 寫回
# `$LASTEXITCODE`(PowerShell 的特殊自動變數,寫入即對呼叫端可見,呼叫端仍可
# `& install.ps1; if ($LASTEXITCODE -ne 0) {...}` 讀到正確值)——★取捨★:若
# 是用 `powershell.exe -File install.ps1` 這種「當成獨立行程啟動」的方式呼叫
# (README 沒教這種呼叫法),因為腳本本身不再呼叫 `exit`,回給作業系統的行程
# exit code 會固定是 0,不會反映失敗;README 教的兩種呼叫方式都是在同一個
# session 內執行(不是啟動新行程),不受此取捨影響。
#
# ★2026-08 Task 15(接續 Task 14,補殘留缺陷)★:Task 14 只修了「結尾」那個
# `exit $LASTEXITCODE`,早期「找不到 python」錯誤分支的 `exit 2` 沒有一併改
# ——這處反而更該修,因為它在錯誤路徑上,使用者最需要看到錯誤訊息的時候
# 視窗反而被關掉,連錯在哪都來不及讀。改法:把整段邏輯包進 `Invoke-Install`
# 函式,錯誤分支印完 `Write-Error` 後 `return 2`(函式層級的 `return`,不是
# `exit`——只結束這支函式,不終止呼叫端 session);本檔案最下方把函式回傳值
# 收進 `$rc` 再寫回 `$global:LASTEXITCODE`,沿用 Task 14 選定的慣例。這段
# 語意同樣沒有真機驗證過,見上方「★誠實聲明★」與 `slim/README.md`〈支援
# 平台〉。
$ErrorActionPreference = "Stop"

function Invoke-Install {
  param($Pkg, $Args)

  $Py = Get-Command python3 -ErrorAction SilentlyContinue
  if (-not $Py) { $Py = Get-Command python -ErrorAction SilentlyContinue }
  if (-not $Py) {
    Write-Error "ERROR: 找不到 python3 或 python 指令——請先安裝 Python 3 再重跑本腳本。"
    return 2
  }

  & $Py.Source "$Pkg\install.py" @Args
  return $LASTEXITCODE
}

$Pkg = Split-Path -Parent $MyInvocation.MyCommand.Path
$rc = Invoke-Install -Pkg $Pkg -Args $args
$global:LASTEXITCODE = $rc
