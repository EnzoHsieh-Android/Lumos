severity: major

審查範圍是整份 diff 的 scripts/lumos、scripts/test_lumos.py 與手冊、筆記各 hunk。實驗都在 `/tmp/lumos-seat-work/code-代碼審minor解綁/正確性-sonnet/`(repo、mut 兩份 clone),沒有動原 repo。

## F1 序號邊界差一的改壞測試照綠,真壞了會直接 IndexError
severity: major
blocking: 是
引句:「elif int(no) > len(decls[path]) - 1:」
file: `scripts/lumos:27979`
file: `scripts/test_lumos.py:9399`

1. 這行是「序號超出宣告數」的唯一界線。它保護 S22 驗收條款(序號超出 → 判不過、不噴例外),也是這案點名的高風險形態,序號 off-by-one。
2. 改壞:把 `- 1` 拿掉,變成 `int(no) > len(decls[path])`。
   - 在 clone 的 `scripts/lumos` 套用後,`python3.14 scripts/test_lumos.py -k t_disposal_code_minor_release` 回 `78 passed, 0 failed`。
   - `-k t_canary_record_finding_source` 回 `32 passed, 0 failed`。
   - 兩支測試都沒抓到。
3. 測試放過的原因:S22 與 S10 只用 `#9`,報告只有 2 條,離邊界很遠。`#0`、`#x` 被別的檢查擋掉。最常見的手誤是「剛好多一條」(2 條的報告寫 `#3`),完全沒測。
4. 改壞後走一遍。報告有 2 條,宣告清單長度是 3(含檔級行),輸入 `x/A.md#3`:
   - 3 > 3 為假,所以通過 `_mr_refs`。
   - 接著 `_mr_accept_errs` 取 `decls[p][3]`。
   - 結果是 IndexError。
   - 閘或記帳會噴 traceback,而不是「第 3 條,但那份報告只有 2 條宣告」。
5. 重現(`probe.py` 在工作目錄):
   - 原碼:`3 ('fail', ['a2 指到 x/A.md 第 3 條,但那份報告只有 2 條宣告'])`
   - 改壞版:`3 EXC IndexError list index out of range`
6. 修法:在 S22 與 S10 各加一個剛好超出一條的案例(2 條的報告給 `#3`),斷言判不過且無 Traceback。

## F2 序號是超過 4300 位的數字時,記帳直接 traceback
severity: minor
blocking: 否
引句:「_FINDING_SOURCE_NO_RE = re.compile(r"[1-9][0-9]*")」
file: `scripts/lumos:27876`
file: `scripts/lumos:27979`

1. 序號的格式檢查 `[1-9][0-9]*` 不限長度。`_mr_refs` 之後直接呼叫 `int(no)`,Python 3.11 以上對超過 4300 位的字串會丟 ValueError。
2. 輸入:`--finding-source a2=<本輪報告>#` 後接 5000 個 9。路徑要是本輪的報告,才會走到 `int()`。
3. 實跑(`cli_probe.py`)結果是 rc 1,最後一行 `ValueError: Exceeds the limit (4300 digits)`,堆疊停在 `_mr_refs`。
   - 沒寫帳,所以不傷帳本。
   - 但違反 S22 與 S16「不噴例外」的寫法。
4. 手改帳也一樣:閘端會噴。
5. 修法:在驗序號格式的地方加長度上限,或在 `_mr_refs` 接住 ValueError 判成格式不對。

## F3 載體的 finding_severities 值是不可雜湊型別時,閘端第九步 TypeError
severity: minor
blocking: 否
引句:「if mine in _SEV_ORDER and _SEV_ORDER[mine] < _SEV_ORDER[top]:」
file: `scripts/lumos:28028`
file: `scripts/lumos:27940`

1. 手改帳,載體帶非空且型別正確的 `finding_sources`,加上 `finding_severities: {"a2": ["x"]}`。
2. 走到 `_mr_own_sev_errs`,`mine` 是 list,`mine in _SEV_ORDER` 丟 TypeError。
   - 實測:`sev-list EXC TypeError cannot use 'list' as a dict key`。
   - 沒有任何接手。
   - 其他讀 `finding_severities` 的地方只檢查最外層是不是 dict,所以這是第九步第一次碰到值的型別。
3. 同類:某列 `severity` 是 list 時,`sevs = {r.get("severity") for r in rows}`(`27940`)同樣 TypeError。
   - 前面的步驟可能已先崩,所以只有 `finding_severities` 的值是這步獨有的第一個崩點。
4. 修法:`mine` 先判 `isinstance(mine, str)`。
5. 這只在手改帳時出現,不傷帳本,所以列 minor。

## manifest 逐條判定

- `cmd_canary` 複雜度 142 > 10:誤報。
  - 這個函式本來就遠超門檻,diff 只多加約 16 個分支。
  - 新增的兩段(旗標格式驗證、載體最後記加核對)我逐段走過,沒找到具體錯誤。
  - 風險在於這個函式已大到難以整體審視,不是這次引入的缺陷。
- `t_disposal_code_minor_release` 複雜度 14 > 10:誤報。
  - 這是情境表式的長測試函式,沒有行為隱患。

## 圖譜鏡頭(固定席節點)

- Issues/canary-record未落盤事件:不影響。新檢查在寫帳前執行,仍走原有的 `_jsonl_append_verified` 寫後讀回自驗。
- Systems/lumos-cli-read(search 預設排除 superseded):不影響,diff 沒碰 search。
- Systems/loop-convergence-recording:不影響。新增的 WHY 行與記帳旗標一致,舊 KEY 沒被推翻。
- Systems/design-loop(處置閘第五步,設計審要 .md 計劃、有 [SN] 要綁測試):不影響。
  - 新步驟 `_disposal_minor_release_step` 接在最後,沒有改既有編號。
  - 第五步對 `code-` 迴圈本來就跳過,沒變。
  - 設計審迴圈進第九步只會印一行「—」,不影響判定。
- Systems/guard-kill、Systems/lumos-cli-lifecycle(INVARIANT):不影響,沒碰 guard kill 的 rc 與 JSON 輸出,也沒碰 re-inject。
- Systems/pitfalls-code-loop、Systems/reversibility-governance-ledger:不影響。
  - 帳本仍只往後加,新欄位只加不改。
  - 「載體記進去後閘端才失敗,這輪只能全折」已寫進計劃的風險面,屬已承認的設計。

## 本案特定鏡頭

① 處置閘回放:不影響。
- 凍結閉包取判定輪全部帳列的 `report_path` 與 `snapshot_path`,第九步讀的正是這批檔。
- 舊 golden 的載體沒有 `finding_sources`,第九步只印「—」並回 skip,舊分支不變,判定不變。
- 不 bump `_REPLAY_ENGINE_REV` 站得住。
- 實跑 `-k replay` 38 條全綠。

② `_gov_event_types_ok` 收緊:不會誤略過合法列。
- 缺欄位或空 dict 都視為合法。
- 只有 `finding_sources` 不是 dict,或值不是字串清單,才被略過,這是預期。
- 實跑 `-k gov` 257 條全綠。

③ cmd_canary 的「載體最後記」檢查:不會誤擋不相干的記帳。
- 只有同迴圈、同輪、帳上已有帶 `finding_sources` 的列時才擋。
- 結局帳(帶 `--outcome`)、沒帶 `--round` 的 light 迴圈、設計審都不會被擋,因為現有帳沒有這個欄位。
- 每次記帳多掃一次帳本,4781 行約 0.06 秒。
- 一個副作用:資安席的「補記同一輪」教法,遇到已有帶來源載體的輪會被擋。
  - 擋下訊息會教「記到下一輪」,救得回。
  - 資安席的 ✗ 訊息沒同步改這句,我沒能構造出具體失敗輸入,所以不列 finding。

## 其他我走過、沒發現問題的項目

- **繞過**:寫側與閘判定一致。
  - 閘端用「恰一筆載體」+ `len(carriers) > 1 → rc2`,與寫側的 `_mr_applicable` 一致。
  - 舊「major 一律折」分支只在 `_mr_applicable` 回 apply 的相同條件下被讓路,沒有「兩邊都放行」的縫。
- **序號正確性**:`_report_items_print` 的序號與 `_mr_*` 的序號口徑相同(去掉檔級行、clean 佔序號、圍欄不算)。標題行號查找沒有差一。
- **路徑正規化**:寫入的路徑與 `report_path` 走同一支 `_ledger_rel_path`,測試也覆蓋 `./`、絕對路徑、子目錄相對路徑。
- **測試抓錯證據**:我另外做了幾個改壞,都能被抓到。
  - 拿掉自填等級下限:S15 紅。
  - 拿掉折入與放行共用檢查:S20 紅。
  - 拿掉載體最後記:S25 紅。
  - 拿掉閘端序號格式檢查:S22 兩條紅。
- **相鄰測試**:實跑 `-k disposal` 263 條、`-k replay` 38 條、`-k panel_probe` 7 條、`-k gov` 257 條,全綠。
- **臨時檔**:`/tmp/lumos-seat-work/code-代碼審minor解綁/正確性-sonnet/` 還在,內有 repo、mut 兩份 clone 和 `probe.py` 等,沒有程序開著。請編排者收貨後依規矩用字面路徑刪除。

最高 severity: major,blocking 條數 1。
