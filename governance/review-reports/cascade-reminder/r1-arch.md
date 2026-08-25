# 架構對齊審查報告——cascade-reminder r1(`/tmp/cascade-reminder-r1.md`)

## 1. doctor soft-check 落點

**Finding 1-A(severity: major,blocking: 是)** 判準:引入第二種做法——同一個 `cmd_doctor` 函式裡已經有一段在掃同一批帳本檔,spec 沒提也沒併,等於平行造第二條掃描路徑,牴觸 d1 自己宣稱的「零新機制」。

Check E2(`scripts/lumos:936` 起)本來就會 `_rcd = _rel_cascade_dir(env)` 後 `for _p in sorted(_rcd.glob("*.jsonl"))` 逐檔 `_ledger_read(_p)`,把 transitions 折成 terminal 事件用來抑制假陽性——這正是 spec PRIOR-ART 點名要借用的兩個函式,只是既有呼叫點不在 spec 引的位置附近,而是嵌在 E2 內部:

引句:「[M3] ledger 抑制:掃 rel-cascade 帳本折疊出 terminal 事件」

file: `scripts/lumos:950`(`_rcd = _rel_cascade_dir(env)` 於 `:954`,`for _p in sorted(_rcd.glob("*.jsonl")):` 於 `:956`)

spec 對這件事完全沒有著墨,只講「借用既有帳本讀取」兩個函式本身:

引句:「既有 doctor soft-check 形態+既有帳本讀取」

file: `docs/lumos-toolchain-knowledge/Projects/連鎖佇列軟提醒_計劃.md:19`

按 spec 現在的寫法照做,實作者大機率會在別處(比如 E3 之後、或獨立新段)重新寫一次「glob `*.jsonl` → `_ledger_read` → 判斷」,跟 E2 裡幾十行前已經存在的同款迴圈各自維護一份對「header 損毀/torn 行」的容錯認知——兩處若日後其中一處改了容錯語意,另一處不會跟著動,正是 d2/d4 想避免的「同一事兩處喊」的鏡像問題(這次是「同一掃描邏輯兩處寫」)。應該併進 E2 那段既有迴圈順手多收集一份「header 或 transitions==0」的統計,而不是新開一段。

## 2. 訊息三段式

**Finding 2-A(severity: major,blocking: 是)** 判準:與既有慣例矛盾——doctor 裡目前沒有任何一個 `warn_soft` 呼叫真的把指令印成獨立一行,d3 要求的形態需要偏離 `warn_soft()` 唯一支援的單行 advice 參數,spec 沒交代怎麼做,而 [T2] 的行為斷言把「獨立指令行」當成可測斷言,兩者會撞。

spec 的目標形態:

引句:「指令獨立一行(`lumos rel-cascade list`)」

file: `docs/lumos-toolchain-knowledge/Projects/連鎖佇列軟提醒_計劃.md:29`

但 `warn_soft(lines, head, advice=None)` 的實作只有一個 `print` 把整句 advice(含指令)印成一行:

引句:`print(f"  {C['B']}建議{C['X']}: {advice}")`

file: `scripts/lumos:496`

現有 doctor 段落無一例外都是把指令嵌在 advice 句子裡(不是獨立行),例如版本提醒段:

引句:「用這個指令把工具鏈和紀律區塊更新到最新:lumos update」

file: `scripts/lumos:1386`

真正做到「指令獨立一行」的是 `prose-lint`(2026-08-25 新增),但它不是走 `warn_soft`,是自己手刻 `print`:

引句:`print(f"    lumos prose-lint {path}")`

file: `scripts/lumos:13720`

也就是說,d3 想要的訊息形態其實是這個 repo 最新的家規(2026-08-22 `tool-output-plain-style`),但 doctor 內部的 `warn_soft` 機制還沒跟上、也不支援。spec 若真要滿足 [T2] 的獨立指令行斷言,implementer 要不就是在呼叫 `warn_soft` 之後手動再 `print` 一行指令(跟 `warn_soft` 的單行 advice 慣例分岔),要不就得改 `warn_soft` 本身簽章——這兩條路 spec 都沒選、也沒提,是實作時真的會卡住或做錯的地方。

其餘部分**對齊**:數字旁講清楚是什麼(例1「2 張連鎖待辦單還沒人看過(最老 21 天)」,計數與天數各自有語意詞綁著,同 Check S/S2/E1 的 head 句式);成功/靜默不佔版面(例5 全判定時完全不印,見下方 1 的補充)——這兩點都跟家規對得上。

## 3. 「零新命令」宣稱與連動守衛

**對齊**(t_docs_command_count):此守衛量的是 argparse 頂層子指令數(`--help` choices),與 doctor 內部多一段 check 無關:

引句:「命令數真值取自 --help choices(非原始碼 regex)」

file: `scripts/test_lumos.py:16643`(守衛定義於 `t_docs_command_count`,`scripts/test_lumos.py:16629`)。T1 不註冊新 `add_parser`,不會動到這條真值,「零新命令」對這個守衛成立。

也沒有找到「doctor N 項檢查」這類會被機械核對的計數守衛(grep 全庫只有敘述性的「一道檢查」用詞,無對應 `check(...)`),訊息措辭本身也沒有掃描型測試(`test_lumos.py` 沒有通用的 wording-scan test,這類判斷目前只靠像本次這樣的人審)。

**Finding 3-A(severity: minor,blocking: 否)** 判準:不確定會不會做錯,取決於 spec 沒指定的段落擺放位置——若新段落文字被插進既有 `[S]`/`[E1]` 兩個標題之間,會落進一個用字串切片抓區間的既有測試視窗內。

引句:`sect = lambda out: out[out.index("[S]"):out.index("[E1]")]`

file: `scripts/test_lumos.py:4631`(屬 `t_doctor_soft_sections_truncate_by_default`)

這個 helper 是拿 doctor 輸出裡兩個字面「[S]」「[E1]」之間的整段文字去數 `"• Systems/S"` 出現次數,不是真正的結構化解析。目前碰撞機率低(帳本檔名格式 `c-<timestamp>-<hex>.jsonl` 不含 `Systems/S` 字樣),但 spec 完全沒有交代新段落要放在 doctor 既有段落序列的哪個位置,若日後有人把它插在 S2 與 E1 中間,這條測試的抓取視窗會悄悄多吃一段不相干內容。建議 spec 補一句「新段落放在 E2 之後」(順帶呼應 Finding 1-A 的併入建議),就能同時避開這個風險。

## 4. 一事一處

**對齊。** 判準:spec d4 的理由本身有查證得到的依據,且沒有找到其他既有位置在「報」這件事——`lumos gov`、weekly 報表腳本、`cmd_rel_cascade_list` 都不輸出「N 張零判定帳本」這種彙總統計,搜遍 `governance/` 下非歷史快照的程式碼與報表也沒有第二個真相源在講同一件事:

引句:「本提醒重報=同一事兩處喊」

file: `docs/lumos-toolchain-knowledge/Projects/連鎖佇列軟提醒_計劃.md:30`

`cmd_rel_cascade_resume` 對損毀 header 的處理確實如 d4 所述指向 E2 兜底(`scripts/lumos:8391` 一帶「header 損毀,root 不可恢復——本 cascade 放棄,交補網 E2 兜底」),d4 的推論站得住。

**但要注意**:這一點跟 Finding 1-A 是兩件不同的事——d4 講的是「重複報給人看」(沒有,對齊),Finding 1-A 講的是「重複掃描同一批檔案的機制」(有,E2 已經掃過一次),兩者判準不同,不要用 d4 的對齊結論去覆蓋 1-A 的問題。

---

## 總結

最嚴重 severity:**major**(Finding 1-A、Finding 2-A 各一條)。
blocking 共 **2 條**(Finding 1-A、Finding 2-A);另有 1 條 minor/非阻擋(Finding 3-A)供實作時參考。