severity: major

我照字面把修訂稿實作成參考程式(只在我的暫存目錄跑過,已刪),再對 `scripts/lumos`、`scripts/test_lumos.py` 和 `docs/.canary-log.jsonl` 實測。

1. 帳上 `quote_rule` 欄位的值域只定義了「有值」「沒有」「不認得」三種,空字串、null、數字、陣列、大小寫都沒定
severity: major
blocking: 是
引句:「有值就照那一版判;沒有這一欄就照舊判準 `legacy`」
file: `scripts/lumos:26311` 附近,`_GOV_FIELD_TYPES`(約 9660 行)沒有 `quote_rule`,帳本讀側不擋型別錯的行。
1. 輸入 `"quote_rule": ""` 或 `null`。照字面讀有三種走法:當「沒有」,於是靜默降回舊判準;當「有值但不認得」,於是判失敗;或寫成 `row.get("quote_rule") or "legacy"`,空字串靜默降級。三種都符合條文,結果不同。
2. 輸入 `"quote_rule": ["full-span-v1"]` 或 `{}`。實作若用 `rule in {"legacy","full-span-v1"}` 或 dict 查表,會丟 `TypeError: unhashable`,處置閘直接 traceback。這個閘的慣例是壞型別 fail-closed 回 rc2(見 `findings` 欄壞值那段),本篇沒要求同樣處理。
3. 輸入 `"FULL-SPAN-V1"` 或 `" full-span-v1"`。條文沒說要不要正規化,「未知值判失敗」的訊息要不要印非字串值也沒說。
4. 測試只有「欄位缺失」和 `future-v9` 兩個案例,上述五種輸入翻不了紅,實作怎麼寫都過。
5. 預期:欄位存在但不是 `legacy` / `full-span-v1` 之一(含空字串、null、非字串),一律判失敗並寫明,不 traceback;只有「欄位根本不存在」才走 legacy。須補條款和測試。

2. 「下一個引句標籤」沒定義是「引句加冒號」還是「引句加冒號再加開引號」,兩種讀法在落單收尾引號上結果相反,其中一種可繞過
severity: major
blocking: 是
引句:「掃到下一個標籤的開頭(或報告結尾)還沒回到零,這條判格式不合」
1. 步驟 1 把後面不是開引號的「引句:」定為「照舊不理」,步驟 3、4 的邊界卻只說「下一個標籤」。
2. 輸入 `引句:「真的原文真的原文真的」這是引句：編造後半」`,我兩種讀法各跑一次。
   - 邊界取任何出現的標籤字樣:尾段在「引句：」處被截掉,後面的落單 `」` 沒被掃到,判錨定,編造後半漏過。
   - 邊界只取標籤加開引號:判落單收尾引號,不合。
3. 〈量測〉第 30 行自己承認「說明文字提到引句：這個詞」有 23 組,所以這個字樣在真報告裡常見,造假者也能故意放進去。
4. 預期:條文寫死邊界是「標籤加緊接的開引號」(與 `n_markers` 的現行計數一致),並加一支測試,輸入就是上面那行。

3. 引句內文本身含「引句:」加開引號的正當引用(引範本、引這份 spec),整條被判兩次不合
severity: minor
blocking: 否
引句:「席位要改引一段不含落單引號的片段。範本寫明。」
1. 輸入 `引句:「如範本所示 引句：「原文原文原文原文原文原文」 後略」`。外層因為碰到內層標籤判未閉合,內層抽出後尾段 `」` 又判落單,一個引用產生兩條不合。舊判準只取到第一個 `」`,可以通過。
2. 〈實務隱患〉只列了引正則裡的落單引號,沒列這種「引範本或 spec 自己引用格式」的情形。本篇 spec 第 20 行、範本 §1 都是這種文字,審查本計劃或範本時一定會踩到。
3. 預期:接受並寫進隱患清單,範本教席位避開。

4. `quote-check --compare-rules` 的命令列在現行 parser 下根本叫不起來
severity: major
blocking: 是
引句:「`lumos quote-check --compare-rules [--since YYYY-MM-DD] [--repo 根]`」
file: `scripts/lumos:53141-53144`,`qc_report` 是必填位置參數,`--spec` 設了 `required=True`。
1. REVISIT 第 25 行寫的 `lumos quote-check --compare-rules --since 2026-10-14` 沒有報告也沒有 `--spec`,現行 parser 直接回 argparse 錯誤 rc2。
2. 條文沒要求把 `qc_report` 改成 `nargs="?"`、`--spec` 改成非必填,也沒說這些組合怎麼處理:`--compare-rules` 加報告、`--compare-rules` 加 `--rule`、沒有 `--compare-rules` 卻帶 `--since`。
3. 預期:條文寫明參數互斥與必填的改法,否則 REVISIT 的指令照抄會失敗。

5. `--compare-rules` 掃帳對讀不到、非 UTF-8、帳本壞行、大帳本都沒定義,而 RETIRE-IF 的決策就吃這個指令的數字
severity: major
blocking: 是
引句:「同一組(報告, 快照)只算一次、讀得到的才算,得 2631 組」
file: `docs/.canary-log.jsonl`(本 worktree 4212 行)
1. 我照同樣口徑(`report_path` 加 `snapshot_path`,沒有就取 `spec_path`)數過:共 3279 組,兩邊都讀得到的有 3259 組,對不上 spec 寫的 2631。〈量測〉的數字用這個口徑重現不出來,算 ⚠。
2. 有 20 組讀不到,另有 1 個檔不是 UTF-8。實作若沿用 `except OSError` 而漏掉 `UnicodeDecodeError`(`cmd_quote_check` 的註解說明這個坑踩過),整個掃描中途 traceback。條文只說「讀得到的才算」,輸出沒要求印「略過 N 組」,數字會悄悄變小。
3. 帳本壞行(非 JSON、不是物件)條文沒提。其他讀帳點都帶 `n_badlines`。
4. 效能:各組快照大小加總約 998MB(約 950 個不同快照)。`_quote_rows` 每次呼叫都重新 `_quote_norm(stext)`,兩版判準共 6500 多次,沒有依快照快取。數萬行帳本會很慢,記憶體也要避免把全部文字留著。
5. 預期:條文要求輸出「略過 N 組(讀不到 a、非 UTF-8 b、壞行 c)」、同一快照只正規化一次、兩種例外都捕。須補測試。

6. `--since` 格式錯誤與時區比對沒定義
severity: major
blocking: 是
引句:「`lumos quote-check --compare-rules [--since YYYY-MM-DD] [--repo 根]`」
1. 帳本 `ts` 全部是 `YYYY-MM-DDTHH:MM:SS+08:00`(4212 行全是,我統計過)。
2. 若實作用字串比對,`--since abc` 因為 `"abc" > "2026..."` 會濾掉所有列,交叉表全 0、rc 0。到了 REVISIT 就是假的「零誤傷」。
3. 輸入 `--since 2026-10-14`、`ts=2026-10-14T05:00:00+08:00`(UTC 是 10-13 21:00):字串比對算進去,走 `_loop_ts_key` 換算 UTC 則排除。本篇 PRIOR-ART 自己批評過這個時區坑,但這裡沒說用哪種。
4. `2026-13-45` 這類不存在的日期、沒有 `ts` 或 `ts` 解析不動的列,是納入還是排除,也都沒說。
5. 預期:格式用 `YYYY-MM-DD` 嚴格驗,不符回 rc2 並印用法;比對用 `_loop_ts_key`;`ts` 無法解析的列要明說歸屬並計入「略過」。

7. 擋下事件的 note 沒帶隨機碼,同秒連撞會被去重折成一次;且「因新判準擋下」沒說怎麼判
severity: minor
blocking: 否
引句:「記帳寫側因新判準擋下載體時,用 `_gate_event_or_warn` 記一筆 `canary` 閘的 blocked 事件」
file: `scripts/lumos:10933` 一帶;該行註解寫「id=事件隨機碼:同一秒連撞兩次不能在 gov 去重時折成一次」,同檔其他三處 blocked 事件也都帶 `id=`。
1. spec 的 note 只列 `quote-rule=full-span-v1` 與類別,沒有 `id=`,同秒兩次擋下會被 `gov` 折成一次,REVISIT 的計數偏少。
2. 寫側擋下的條件是「有任何一條錨不到」,其中舊判準本來也會擋的不少。若每次擋下都記 `quote-rule=full-span-v1`,事件會混入舊判準照擋的普通錨不到,REVISIT 的「新判準擋下數」被灌水。要區分就得另跑一次 legacy,條文沒要求。
3. 預期:note 加 `id=`,類別欄區分「只有新判準擋」與「兩版都擋」。

8. 格式不合列的內容與欄位契約沒定,影響 `seat-check` 和 `--json` 輸出大小
severity: minor
blocking: 否
引句:「`seat-check` 用 `_QUOTE_RULE_WRITE`(它只拿抽出的引句文字比材料範圍,格式不合的列照舊跳過)」
file: `scripts/lumos:26789-26790`,seat-check 靠 `q.get("malformed")` 跳過格式不合的列。
1. 步驟 6 拿掉了「差額補列」,舊版補的那列有 `quote` 佔位字串和 `malformed: True`。新判準對未閉合、落單收尾兩型的列要不要帶 `malformed: True`,條文沒寫。
2. 落單收尾那型若只標 `ok: False` 而漏了 `malformed`,`seat-check` 會把它當一般引句去比材料範圍,誤報成 `out_of_scope` 並寫進 `--ledger`。
3. 未閉合列的 `quote` 若存「到下一標籤(或報告結尾)為止」的整段,單條可達整份報告大小;`cmd_quote_check --json` 會原樣印出(目前人讀版只印前 60 字)。
4. 預期:兩型都明寫 `malformed: True`,並限制 `quote` 欄長度(例如截 200 字加標記)。

9. 帳上的章可以靠改帳刪除,而條文把它當信任根,卻沒進〈實務隱患〉
severity: minor
blocking: 否
引句:「沒有這一欄就照舊判準 `legacy`——沒有這一欄的帳是舊版程式寫的」
file: `scripts/lumos:9650` 起的註解說治理帳在簿記白名單裡,直接提交一行不會讓代碼審留痕失效;canary 列沒有自身雜湊。
1. 輸入:把某筆帳的 `quote_rule` 刪掉,該輪即降回舊判準,新判準對這輪失效。
2. 這不比現況差,但「沒有章 = 舊版程式寫的」是假設,不是保證。
3. 預期:列為已知限制,並說明靠凍結回放(閉包整行)偵測。

已讀,無 finding:
- 零發現輪:處置閘在無載體且全部 findings 為 0 時略過引句檢查,寫側也不會對它蓋章。與條文「零發現輪不驗引句」一致。
- 同一輪多筆帳、載體與非載體章不同:處置閘規定一輪只准一筆載體,只讀載體的章。條文是自洽的。
- 報告裡上百個標籤、標籤緊貼、標籤在檔尾、極長未閉合引句:我的參考實作都是線性時間。標籤在檔尾後面沒有開引號,算不了一條引句,不影響前一條的尾段。
- 緊貼的 `引句：「甲…」引句：「乙…」` 各自正常抽出。

實務隱患逐類:
- 資料完整性:有,見 1、5、9。
- 可用性或當機:有,見 1(`TypeError`)和 5(`UnicodeDecodeError`)。
- 效能:有,見 5 第 4 點(快照每次重新正規化)。
- 可觀測性:有,見 6 和 7。
- 金流:無,本篇不碰。
- 對外送出:無,只在本機讀。

總結:最高等級 major,blocking 共 5 條
