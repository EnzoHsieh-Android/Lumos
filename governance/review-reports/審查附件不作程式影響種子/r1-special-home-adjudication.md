Finding 1  
severity: major  
blocking: 是  
引句:「f2 = f2.strip().strip('"')」  
file: `scripts/lumos:41281`  
最小重現: `python3 scripts/lumos impact --diff HEAD~1..HEAD --repo . --sync-check --json`，穩定得到 `TypeError: a bytes-like object is required, not 'str'`。NUL 改動使 `r.stdout` 成為 bytes，但 `--sync-check` 仍以字串處理。

Finding 2  
severity: major  
blocking: 是  
引句:「check('特殊路徑的家仍必推', {'Systems/Special0.md', 'Systems/Special1.md'} <= pins, str(pins))」  
file: `scripts/test_lumos.py:23110`  
最小重現: `python3.14 scripts/test_lumos.py -k impact_diff_special_paths` 得 3 passed、1 failed；精確種子與事故通過，只有家斷言失敗。fixture 呼叫 `_nh_node` 時未傳 `about`，實際產生 `about_code: []`；而正式流程在沒有 home-map 項目時直接返回空家，因此此斷言缺少「原本確為有效家」的前置條件。

分類新增是否令有效家遺失：已讀,無 finding。現有證據顯示換行與 tab 路徑都被精確保留為 seed，事故也命中；家失敗來自 fixture 沒註冊家。

換行 basename 的既有表示限制：已讀,無本次分類 finding。literal-block `about_code` 可無損登記，但 `_home_scan_text` 排除該欄位，且 `INLINE_CODE_RE` 不跨換行，所以既有格式無法確認該家；不應因此擴充全域 parser。

最小有效驗收口徑：

- 保留換行 basename 的精確 seed 與 incident 驗收。
- tab 路徑用 `about_code` 清單加正文 inline code 建立有效家，先以單檔 impact 證明 pinned，再驗 diff 後仍 pinned。
- 另用「換行在目錄、basename 為唯一 `tool.py`」搭配 literal-block `about_code` 與正文裸 basename，驗證另一個有效家。
- 不對換行 basename 宣稱家必推。

總結最嚴重 severity: major；blocking: 2 條
