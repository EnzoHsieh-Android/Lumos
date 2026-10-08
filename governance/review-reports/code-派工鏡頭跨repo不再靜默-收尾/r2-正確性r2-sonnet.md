severity: minor

我有看到「lumos 自動附加」段,共 29 篇:8 篇有摘要(pitfalls-code-loop、lumos-cli-read、lumos-cli-lifecycle、reversibility-governance-ledger、guard-kill、測試假綠形態、loop-convergence-recording、design-loop),其餘 21 篇只列名。

## F1 找用法的正規式只認 `_plain_label(` 或 `_frame_injected(` 直接呼叫,別名與帶空格寫法抓不到
severity: minor
blocking: 否
引句:「             if _re.search(r"\b_(?:frame_injected|plain_label)\(", f.read_text(encoding="utf-8"))]」
佐證:file: `scripts/test_lumos.py:17041`(臨時 clone 4286696f 上,即 diff 的 `users = [...]` 那段)
失敗場景:
- 在沒抄區塊的 `check-graph-sync.py` 末尾加一行 `_pl = _plain_label`,守衛仍 14 passed、0 failed。這支檔進不了 `users`,所以不會被檢查有沒有區塊。
- 加 `return _plain_label ("a")`(括號前有空格)也是全綠。
- 真的執行這支掛鉤,第一次碰到 `_plain_label` 就 NameError,跟上一輪抓到的派工鏡頭 NameError 同形。
- 這兩種寫法不符合 repo 現有風格(ruff 會格式化掉空格),實際發生機率低,所以只列 minor。

歸因:有證據的原有漏查。修前版 12b10db1 的測試同樣全綠,因為它只掃寫死的四支。修後版沒有因此變差。
查證命令與結果:
- 兩版都用 `python3.14 scripts/test_lumos.py -k injection_paths_are_framed`,先在 `check-graph-sync.py` 追加 `_pl = _plain_label`。
- 修後版:`14 passed, 0 failed`。
- 修前版(把 `12b10db1` 的 `test_lumos.py` 換進來):`13 passed, 0 failed`。
- 每次跑完都用 `git checkout` 還原。

## 已驗主張(修補鏡頭)

以下都在臨時 clone 的 4286696f 上跑,每次破壞後還原,`git status` 乾淨。

**repair 案例(修後版紅,修前版是否紅見各條)**

| 破壞 | 修後版 | 修前版(12b10db1) |
|---|---|---|
| memory-sweep.py 把 `_plain_label` 的 `cap=120` 改成 `121` | 紅(`2 種版本`,memory-sweep.py 單獨一組) | 綠(13 passed),修補確實補上了這個缺口 |
| 拿掉 dispatch-lens-hook.py 整段區塊 | 紅(`missing=['dispatch-lens-hook.py']`) | 紅(清單上每支檔都有框常數那條) |
| check-graph-sync.py 新增 `_plain_label("a")` 呼叫但不抄區塊 | 紅(`missing=['check-graph-sync.py']`) | 綠,修補確實補上了這個缺口 |
| `scripts/lumos` 的 `_plain_label` 把 `cap=120` 改成 `119` | 紅(`lumos` 單獨一組) | 未跑(修前版只比框常數,推論綠) |

**preserve 案例**
- 現況六份區塊(ci-status、dispatch-lens、impact、lumos-entry、memory-sweep、lumos 本體)逐字相同,守衛綠(14 passed)。
- 同一支測試的其他斷言行為不變:框常數一致、每條 additionalContext 都框了、框只包專案值,全部仍綠。
- 六份區塊逐一單獨執行,`_frame_injected` 與 `_plain_label` 都能跑。區塊不依賴區塊外的名稱,所以逐字複製不會漏掉依賴。
- 各檔的起訖標記都是 2 個開頭相符、1 個結束標記。起標記帶冒號,結束標記不帶,所以 `^# ── ★注入框:` 不會誤抓結束行。非貪婪比對取得到完整區塊。

**其他路徑**
- 註解行寫 `# 見 _plain_label(x) 的說明` 會讓守衛假紅(`missing=['check-graph-sync.py']`)。這是往嚴的方向,現況沒有這種註解,也不是缺陷。
- `len(users) &gt;= 4` 合理:目前 5 支,下限只是防 glob 找不到檔。
- 消費端沒有 hook 原始碼時,前面的 `_SrcOnly` 已先擋掉。`lumos` 本體讀不到時,`_load_lumos` 早就先失敗,不會多一個新的崩潰點。

**未驗範圍**
- 區塊內容與區塊外邏輯的語意耦合,例如區塊外某個函式依賴區塊內的常數。
- 掛鉤檔含 CRLF 或縮排版的標記行。
- 本輪沒跑全套測試。
- 角色卡:be-api-compat、be-authz 這次都不適用。diff 只動測試與筆記,沒有端點,也沒有對外 API 欄位變動。

**三問**
1. 原問題(守衛只看寫死清單、只比框常數)的修復效果有行為證據:memory-sweep 改一字紅、新增未抄區塊的呼叫紅,修前版對這兩個都綠。
2. 修補處的正常路徑、錯誤路徑與相鄰呼叫路徑都成立:現況綠,漏抄與本體改動紅,其餘 13 條斷言不變。
3. 新發現的別名與帶空格呼叫,修前、修後都是綠,屬於原有漏查,不是修補造成的回歸。

**圖譜鏡頭**
- repair 只動 `scripts/test_lumos.py` 與兩篇筆記,沒碰 `scripts/lumos` 或 hook 本體。
- 各節點宣稱的行為與合約(search 排除 superseded、re-inject byte-equal、guard kill 的 rc 優先序等)都沒有被這份差異破壞。
- 筆記改的句子與守衛新行為一致:codex-harness 的 PITFALL 修法欄寫「自動找」,計劃筆記的描述也相同。

總結:這次修補確實把「少抄區塊」和「抄了但清理函式本體被改」兩種情況都擋住了,只剩用別名或括號前加空格呼叫的寫法偵測不到,是原本就有的小缺口,不影響這輪放行。
