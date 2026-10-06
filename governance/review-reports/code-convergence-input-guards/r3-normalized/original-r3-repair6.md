severity: major

固定 HEAD 已核對為 `95735eff7f3e17c930d43eecde5dd9d7c4fe9eff`。本席只確認指定比較片段存在下列問題；不把它歸因為某次目標修補，也不代表整輪無回歸。

repair6-F1

severity: major

blocking: 是

引句:「    check("S6 只掛壓縮一個事件",」

觀察：`t_context_plugin_files_valid` 的禁用事件規則與事件枚舉都只辨識單引號。合法 TypeScript `on("prompt.submit", bad)` 同時避開禁用檢查與「只掛 session.compact」清單；而程式已明載 CI 沒有 `claude`，因此 CI 不會由後面的 `plugin validate` 補抓。

判準：合約宣稱外掛不得修改使用者輸入且只能掛 `session.compact`，所以雙引號、單引號必須得到相同判定；禁用事件不得因字面引號形式改變而放行。

具體輸入路徑：在 `mods/claude/lumos-context/hooks/register.ts` 同時存在 `on('session.compact', ok)` 與 `on("prompt.submit", bad)`。

file: `scripts/test_lumos.py:74578`

file: `scripts/test_lumos.py:74584`

file: `scripts/test_lumos.py:74586`

命令：

```text
python3 -c 'import re; code="on(\047session.compact\047, ok); on(\"prompt.submit\", bad)"; banned=r"\047prompt\.(compose|section|context|attachment)\047|\047prompt\.submit\047"; events=r"on\(\047([a-z.]+)\047"; print("banned_match=", bool(re.search(banned, code))); print("events=", sorted(set(re.findall(events, code))))'
```

原輸出：

```text
banned_match= False
events= ['session.compact']
```

後果：在無 `claude` 的 CI，能改寫使用者輸入的新增 hook 仍可通過這支安全合約測試。這是已重現的檢查器假綠，不是只由措辭推測的疑慮。

建議：共用同一個同時接受 `'`／`"` 的事件擷取器，再對完整事件集合做白名單比較；補一個雙引號 `prompt.submit` mutation，要求測試確實翻紅。

固定合約逐條回答：

1. design-loop 審材必須為 `.md`、條款綁測試：本片段未改執行閘，片段層不影響；整輪未實跑，仍未判定。
2. search 預設排除 superseded、不排 stale：沒有落在相關函式或呼叫者的新增行，不影響。
3. code-loop bound-tests 紅／懸空／偽證據／unfilterable 擋下：只改手冊敘述，沒有修改執行閘，不影響。
4. guard-kill rc 優先序：沒有相關新增行，不影響。
5. guard-kill JSON 純度：沒有相關新增行，不影響。
6. deinit 不得刪授權檔：沒有修改卸載白名單或刪除流程，不影響。
7. vendored 檔 SPDX／主程式 MIT 全文：沒有新增該集合的產品檔，不影響。
8. bug 釘須「現場成立＋翻紅」：被 repair6-F1 破壞；新增測試對明確禁用事件存在可重現假綠。

pitfalls manifest：沒有 claim 的 `file:line` 落在本片段新增行，因此本席未選取任何 claim；不把 manifest 當雙版本新增告警判定。

修復／保留／新發現三問：

- 治理帳與跑滿回顧根因族  
  修復候選：治理帳符號連結／非一般檔 fail-closed，以及回顧路徑上層捷徑守衛。  
  保留候選：尚未達 cap 的 `canary record` 仍能正常記帳。  
  結果：兩者均未判定；函式、CLI 呼叫者與帳本合約雖已從 patch 獨立選案，但沒有同案例兩版實跑證據。

- Claude 多外掛生命週期根因族  
  修復候選：`_sync_claude_plugin`／`_teardown_claude_plugin` 對兩支外掛逐支安裝、驗證與移除。  
  保留候選：既有 `lumos-ledger` 可獨立成功，另一支失敗不應阻斷它。  
  結果：修復與保留均未判定；新發現為 repair6-F1。

- 審查修補證據流程根因族  
  修復候選：每個根因分別記修補案例與保留案例。  
  保留候選：既有 cap、處置閘與輪數語意不變。  
  結果：只確認文字新增，沒有可比較的兩版執行結果；不判定流程已修復或已保留。

最小測試曾嘗試：

```text
python3 scripts/test_lumos.py cap_retro_r3
python3 scripts/test_lumos.py cap_retro_r4
python3 scripts/test_lumos.py install_registers_context_plugin
python3 scripts/test_lumos.py lumos_plugin_install_edge_cases
```

四者皆在測試執行前退出；原輸出末行：

```text
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/private/tmp/lumos-future-repair-regression-research']
```

已讀材料：

- `r3-segments/repair-6.patch`：1141 行
- `r3-scope-binding.txt`：15 行
- `r3-graph-lens.txt`：57 個邏輯行
- `r3-pitfalls.json`：198 行
- `r3-test-layers.txt`：0 行
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- 指定必讀合計：1644 行
- `AGENTS.md`：97 行規範
- `lumos-code-loop/SKILL.md`：70 行規範

額外定點上下文：

- `scripts/lumos`：140 行檢索輸出
- `scripts/test_lumos.py`：62 行檢索／helper 上下文
- 合計 202 行，超過 136 行上限 66 行；依派工規則，依賴超額上下文的正向結論全部列為未判定，需另拆乾淨席覆核。本 finding 僅依指定 patch 與獨立最小判式重現。

最高級：major；阻擋數：1。

三問未判定範圍：全部修復與保留候選的雙版本行為、四組未啟動的命名測試，以及 repair6 以外的整輪來源與共同變更。