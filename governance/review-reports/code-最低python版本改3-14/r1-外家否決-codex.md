severity: major

## F1 shell 第一跳忽略 `LUMOS_PYTHON`

severity: major  
blocking: 是 — 唯一合格直譯器已明示時，安裝器與掛鉤仍誤判成沒有 Python 並擋下。  
引句:「_lumos_any_python || { printf '%s\n' "$_LUMOS_NO_PY_MSG" >&2; exit 2; }」  
file: `install.sh:9`  
file: `scripts/hooks/pre-push:76`

1. 七份相同的 `_lumos_any_python` 只搜尋命令名稱與固定目錄，完全不讀 `LUMOS_PYTHON`。因此只有自訂位置 3.14、沒有 PATH 別名時，S1 指定的 pin 與錯誤訊息提供的逃生路徑都無效；pre-commit、pre-push 與安裝入口會在 lumos 本體啟動前擋下。

2. 最小重現：

```sh
env -i PATH=/definitely-missing HOME=/tmp \
  LUMOS_PYTHON=/opt/homebrew/bin/python3.14 \
  LUMOS_PYTHON_SEARCH_DIRS=/definitely-missing \
  /bin/bash install.sh
```

輸出：

```text
rc=2
找不到任何 python(試過 python3.14、python3.15、python3.16、固定位置、python3、python、py)。
...
裝在別處就設 LUMOS_PYTHON=<那支 3.14 的絕對路徑>。
```

3. 第一跳必須先接受並執行可用的絕對 `LUMOS_PYTHON`，否則它宣稱的修復方式本身不可用。

## F2 找不到時沒有列出各候選結果

severity: minor  
blocking: 否 — 正確地回 2，但違反 S2 的診斷輸出合約。  
引句:「if why not in ("不存在", "沒有這個指令"):」  
file: `scripts/lumos:183`

1. `_py_resolve` 刻意丟掉「不存在」與「沒有這個指令」兩種結果；因此 `_py_floor_message` 無法列出 `python3.14`、`python3.15`、固定位置、`python3`、`python` 各自的結果。

2. 最小重現：

```sh
env -i PATH=/definitely-missing HOME=/tmp \
  LUMOS_PYTHON_SEARCH_DIRS=/definitely-missing \
  /usr/bin/python3 scripts/lumos --version
```

輸出只剩：

```text
rc=2
找過的候選:
  uv python find:沒有 uv,或 uv 找不到 3.14
```

實際也試過的其他候選全部消失，使用者無法區分「不存在」與其他失敗。

已看,無 finding：3.9 語法解析與舊版啟動重跑；實際以 macOS Python 3.9.6 編譯三類檔並成功重跑 `lumos --version`。

已看,無 finding：`{python}` 集中代入、精簡版版本閘剝除、doctor/enforcement 檢查。

已看,無 finding：掛鉤註冊引號、Windows 啟動器與 PowerShell 候選流程、CI 3.14 與 Ruff py39 守衛。

最嚴重等級 major，blocking 共 1 條。