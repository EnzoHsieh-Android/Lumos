severity: major

## F1 「另有 N 行沒列(改完這些再提交會再列)」的承諾在提醒發出時已經不可能成立
severity: major
blocking: 是
引句:「另有 2 行沒列(改完這些再提交會再列)」
file: `scripts/hooks/pre-commit:230`
1. 提醒只在提交前掛鉤印,rc 0,提交照樣成立(〈做法〉3「只有提醒時印完、記完帳就回 0」)。
2. 下一次提交(或 amend)時,`--staged` 的取新行是 `git diff --cached -M -U0`(`scripts/lumos:24801`),只含「索引對 HEAD」的新增行。沒列的那幾行已在 HEAD 裡,不再是新行。我在暫存 repo 實測:提交含「還沒做」的行後再 amend,`git diff --cached` 只剩 amend 新加的行。
3. 結果:每次提交只有排序最前的 3 行會被看見,其餘永遠不會再被提醒,只留在帳上 `shown=false`。spec 自己量到工具鏈 11 個提交藏 26 行、rtb 182 藏 11 行、rtb 593 藏 33 行。
4. 括號那句是對寫的人的錯誤承諾(S5 還把字樣逐字釘死)。它也讓「最多印 3 行」這個折法沒有落實:被藏的行既不被提醒,也不進〈做法〉7 的準度、照做率分母(只算 `shown=true`)。
5. 修法二選一:拿掉括號承諾並寫明藏起來的行不會再列;或印一個能看全部的入口(例如指令 `lumos note-shape --staged --all-hints`,或提高上限)。

## F2 `hinted` 的 4 KB 丟欄位順序丟完仍可能超過 4096,S10「整行 ≤ 4096」照字面不可滿足;「估約 3.5 KB」也偏低
severity: major
blocking: 是
引句:量測資料裡一次提交最多 10 行提醒,估約 3.5 KB。
file: `scripts/lumos:1228`
1. `_gate_event` 用 `ensure_ascii=False`,中文按 UTF-8 每字 3 位元組,沒有長度上限(4096 只在 `_ledger_append`:15885)。
2. 我用 spec 的欄位組事件,路徑取 `docs/lumos-toolchain-knowledge/Projects/…_計劃.md` 約 75 位元組,excerpt 為 60 字加兩個「…」。
   - 10 行、10 篇:未截約 4.9 KB、最多約 5.8 KB,不是 3.5 KB。
   - 30 行、30 篇:丟完全部 excerpt 與未印筆數後仍 4227,再丟已印的 excerpt 是 3417。
   - 50 行、50 篇:丟到第三步(已印 excerpt 也丟)仍是 5077。
3. 原因:`nodes`(最多 50 篇)沒有任何一步會截,而且是最大的固定成本。
   - 先例(`scripts/lumos:29430-29443` 舊句檢查)最後有「丟光還超過 → nodes 截到 20」,這裡少了這一步。
   - 〈做法〉4 寫的三步做完後沒有「仍超過怎麼辦」,S10 的斷言(整行 ≤ 4096)在大批提交(搬移、拆篇、rtb 那種 33 篇一次改寫)必紅。
4. 第一步就要動作的門檻其實常態就會到(10 行就過),「估約 3.5 KB」不能當作不用動的依據。
5. 修法:比照舊句檢查加第四步「nodes 截到 20 並記 truncated」,再超過就照寫或丟 hints 只留 total;S10 補一個 50 篇長中文路徑的案例。

## F3 英文 `n't` 分支在參考實作裡永遠不可達,spec 文字與 S9 逐句相同的要求互相矛盾
severity: minor
blocking: 否
引句:`not`/`no`/`n't` 後面 40 字內、不跨 `.;,!?` 接 `yet`
file: `governance/eval/negation-revisit/neg_revisit_measure.py:160`
1. 正則是 `(?<![A-Za-z])(?:not|no|n't)…`。`n't` 前面必然是字母(isn、hasn、don),所以被 lookbehind 擋掉。
2. 我用 `classify_v3` 實測:"It isn't wired yet."、"The gate hasn't shipped yet"、"don't have it yet" 全部回 None;"this is not wired yet"、"There is no X yet" 才算。
3. 照 spec 文字實作(認縮寫)的人,與 S9 要求的「對同一批例句逐句相同」會在縮寫句上分歧。S1 的例句沒有縮寫,測試抓不到。
4. 修法:要嘛把 spec 那句改成「`not`/`no` 後面…(縮寫 n't 不認)」並補「isn't … yet → 不算」的例句,要嘛在量測程式改 lookbehind 重跑報告。英文本來就沒量準度,放行理由成立。

## F4 〈實務隱患〉說帳裡的片段「本來就在 repo 裡」,與〈做法〉4 自己的說法矛盾
severity: minor
blocking: 否
引句:資安(不碰):只讀提交索引裡的筆記;帳裡的片段就是筆記原文,本來就在 repo 裡
file: `scripts/lumos:1228`
1. 〈做法〉4 說 excerpt 存在的理由是「照提醒當場改掉、從沒上主線的句子,只有帳上這一份原文」,也就是帳保存了不在 repo 裡的內容。
2. 帳 `docs/.governance-log.jsonl` 是被追蹤、會被推上去的檔。寫的人若在含「還沒」的行裡貼了不該外流的字(金鑰、客戶名),看到提醒後刪掉再提交,那 60 字仍永久留在帳裡。
3. 修法:把隱患那句改成「片段可能包含從沒進主線的原文,寫入前用既有的秘密掃描字樣過濾,或明寫接受」,不需要擋上線。

## 已讀無 finding 的檢查點
- 句子在表格、標題、清單項、摘要行、圍欄旁、同一行兩個否定字眼、中英混:用 `classify_v3` 與 `_revisit_split`、`_visible_lines`、`_notelines_regions` 實測,判定與〈做法〉1-3 一致;搬成 `- REVISIT:`、`> REVISIT:` 的清單或引用形式 `_revisit_split` 認得。
- 日期式前綴躲提醒:〈誠實界線〉已明講並在〈做法〉7 分開計數,已讀,無新 finding。
- 治理帳寫不進去:`_gate_event` 的 `OSError` 回 False、`_gate_event_or_warn` 印 `telemetry-write-failed`、沒有 `docs/` 回 None,與 S4 描述一致。
- 提醒失敗不影響 rc:接得住的例外都在 try 裡,`cmd_note_shape` 現有結構(早退、`blocked`/`warned` 記帳順序)與〈做法〉3 相容。

最高等級:major;blocking 共 2 條
