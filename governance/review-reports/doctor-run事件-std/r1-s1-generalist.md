# doctor-run事件-std r1 席1(generalist)審計報告

角色:獨立第三方審計,對抗性但憑事實。範圍:whole-doc — undefined behavior / contradictions / unsupported claims。

## 背景核對(light r1 兩條修正紀錄——先驗證有沒有真的收斂)

- **blocker(「隱藏」無機制,`_is_advisory` 只折 warned)**:已修。設計節明確寫「★在去噪摺疊之前、以 gate 名直接濾,不是靠 `_is_advisory` 摺疊——該摺疊只認 `kind=="warned"`,新事件是 `ran` 不會被折★」。核對 `scripts/lumos:3040-3041` 的 `_is_advisory` 定義(`kind == "warned"`)與新事件 `kind: "ran"` 確實不會被摺——原 blocker 描述的機制缺口已補上明確過濾語意。**但此修正的落點本身另生一個新問題,見下方發現 1。**
- **major(事件鍵應為 `note` 非 `detail`)**:已修。設計節寫 `{"gate": "doctor-run", ..., "note": "..."}`,核對 `scripts/lumos:441`(`_append_governance_log` 用 `**e` 原樣寫入任意鍵)與 `scripts/lumos:2992`(`.governance-log.jsonl` mapper 讀 `d.get("note", "")` 映成 `detail`)——欄位名用 `note` 是對的,寫入與讀取兩端一致。

## 發現 1(major)——「--stats 照列」的實作指示與自身要求矛盾,literal 實作會斷

設計節指示:過濾動作要「在去噪摺疊之前」對 `gov` 時間軸「以 gate 名直接濾」,同段接著要求「`--full` 與 `--stats` 照列(stats 要看得到它才能當棘輪分母)」。

引句:「在去噪摺疊之前、以 gate 名直接濾」

問題:`cmd_gov` 裡时间轴顯示與 `--stats` 共用同一個 `ded` 變數——`ded` 在 `scripts/lumos:3029-3037` 建好(dedup + node 縮限),`scripts/lumos:3040` 起的去噪摺疊區塊直接消費 `ded`,而 `scripts/lumos:3142` 的 `_render_gov_stats(_raw, ded, loaded, since_days, cutoff, node)` 用的是**同一個** `ded`(僅另建 `_raw` 對應原始行,`ded` 沒有另複製一份給 stats)。

設計節指示的落點(「去噪摺疊之前」)恰好就在 3040 行之前、3142 行之前——如果照字面實作成「`ded = [r for r in ded if full or r["gate"] != "doctor-run"]`」這種在摺疊前先濾掉 `ded` 列表本身的寫法(這是「以 gate 名直接濾」最直覺的讀法),`doctor-run` 就會在餵進 `_render_gov_stats` 之前已經從 `ded` 消失。後果:`_render_gov_stats`(`scripts/lumos:2908-2949`)的 `agg` 是靠遍歷 `(rows, "raw")` 與 `(ded, "ded")` 兩輪組出來的(`scripts/lumos:2920-2929`)——`raw` 桶仍有 `doctor-run`(因為 `_raw` 沒被這層過濾動到),但 `ded` 桶永遠是 0。該 gate 仍會出現在 stats 表(不會落入「未出現清單」),但「去重後筆數」欄會**恆為 0**,而設計節自己講的用途正是「stats 要看得到它才能當棘輪分母」——分母被砍成 0 等於這個欄位對 doctor-run 永遠失能,直接違反同一段文字自訂的驗收條件。

也就是說:文件同一段話裡,「过滤放在摺疊之前(對 `ded` 動手)」與「stats 照列且要當分母」兩句字面上互斥;文件沒有交代「過濾只能作用在顯示迴圈的印出動作,不能動 `ded` 本身/或要在傳給 `_render_gov_stats` 之前把 `ded` 複製一份分流」這個關鍵區隔,undefined。測試清單第 3 條「`gov --stats` 列出」不足以擋住這個坑——因為 gate 名確實還會出現在表裡(只是去重欄位數字錯),一個只斷言「gate 名有沒有出現」的測試會綠燈放過。

建議:文件明確加一句——過濾只發生在 timeline 的「印出」步驟(即 `full` 分支與非 `full` 分支各自的 print 呼叫處按 gate 名跳過),`ded` 本身(進 `_render_gov_stats` 那份)維持不動;或者測試 4 之外再加一條斷言 `--stats` 表格裡 `doctor-run` 那列「去重後筆數」欄位 > 0(不能只驗證「出現在清單」)。

## 發現 2(minor)——「恆」/「每次都固定寫一筆」的用詞比實際保證強

引句:「乾淨 run 因此恆有一筆可寫」

`_append_governance_log`(`scripts/lumos:420-441`)自己文件化的行為是:非 git repo、或 `git rev-parse --short HEAD` 拿不到 commit → 直接 `return`,不寫、不報錯(`scripts/lumos:421-424` 空事件早退;`scripts/lumos:431-433` 拿不到 commit 早退)。緣起段與設計節用「恆」「每次 `--ci` 都固定寫一筆」這種無條件措辭,但這個保證實際上是「有 git 且拿得到 HEAD 才恆有一筆」——條件被文件省略。這不是本案新引入的缺陷(既有其他 gov 事件本來就受同一條件限制),但文件的「唯一真相」敘述本身对外過度宣稱了確定性,屬 unsupported claim,建議補一句條件限定或至少不用「恆」這種絕對詞。

## 其餘核對(未發現額外 major/blocker)

- `_KNOWN_GATES` 新增 `doctor-run` 為字面值寫法(非動態拼字串),符合 `t_gov_stats_gate_drift` 的「動態 gate 寫點恰為 1 處」釘子(`scripts/test_lumos.py:3047-3063`),不會誤觸發。
- `_STATS_NODE_SEMANTICS` 確實不需要新增——`nodes` 恆空,`_render_gov_stats` 的 `nd = "n/a" if not a["nodes"] else ...`(`scripts/lumos:2936`)已經如設計節所述印 n/a。
- 落點位置(`_append_governance_log` 呼叫前、`ci` 分支內)不影響 `issues`/`rc`/純 `doctor` 路徑——核對 `scripts/lumos:1327`(`if ci: _append_governance_log(...)`)與 `issues` 計數只由 `warn()`(hard)累加(`scripts/lumos:461-468`),`gov_events` 是獨立列表,兩者不互相污染,「不改判定、不改 rc、不改純 doctor」的宣稱成立。
- `docs/.governance-log.jsonl` 已在 `_BOOKKEEPING_FILES`(`scripts/lumos:10299-10300`)白名單內,code-loop「只准簿記檔 commit」豁免不受影響;`.github/workflows/ci.yml:25` 的 `doctor --ci` 在 ephemeral runner 上執行,寫入不會被 push 回 repo,與現有其他 gov 事件行為一致,非本案新增風險。

## 嚴重度統計

blocker: 0 | major: 1 | minor: 1
