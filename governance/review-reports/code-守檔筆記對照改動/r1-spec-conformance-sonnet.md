severity: clean

鏡頭:實作是否照計劃(spec-conformance-sonnet)。主審 r1-snapshot-code.patch,對照〈做法〉0–6、條款 S1–S14、〈實作紀錄〉。

沒有找到會做出跟計劃不同行為的地方,不湊數。下面是逐項核對過的範圍與實跑證據。

核對過、與計劃一致:
- 〈做法〉0:比對用 NFC、問 git 用原樣路徑並帶 --literal-pathspecs(改動清單、組 diff、列紀錄目錄三處都有);行用 split("\n") 切、行號靠右補 4 格接「| 」。
- 〈做法〉1:範圍解析加 reasons 參數且給了就不印不記帳,既有呼叫端不變;起點算不出、頂端已在主線、刪除分支、淺層 clone 的分流跟〈做法〉4 一致(實跑:全 0 終點記 none、終點找不到記 skipped、格式錯記 skipped、皆 rc0);改到的檔不經 _nodehome_required、家取兩邊、碰過的筆記走逐提交的 _notes_touched_in_range(_notes_status_flipped 改呼叫它,行為不變)。
- 〈做法〉2:兩個指紋各一支共用函式;對照指紋不含筆記 blob 與範圍;材料指紋含 diff;diff 組法固定參數加 -M(〈實作紀錄〉已列);3、1、0 行依序試再平均截斷;範本與計劃〈附錄〉V3 機械比對,只多計劃要的兩樣附加;範本載入與填字抽成共用函式、一次掃描替換;sonnet/codex 分用途。
- 〈做法〉3:json 區塊抽法、逐項收(布林不算整數、行號範圍、重複只留第一次、quote/why 截 500)、來源不符照收標 provenance_ok: false、範本版本不符整份拒收、紀錄檔名與原子寫入、簿記豁免。實跑 record:布林行號與超出行數各被丟並印原因、紀錄檔寫出。
- 〈做法〉4:reread-check 恆回 0、輸出走標準輸出、最外層只接 Exception、開關四種壞設定與 block 照 warn、LUMOS_SKIP_REREAD_CHECK 記 skipped-env、reminded/none/covered/skipped 事件。實跑 S6 情境:對一篇 record 並提交後再跑 check,該篇不再被列(5 篇剩 4 篇)。掛鉤段位置在存量漂移之後、標記行獨立一行、只在 130 交給 pp_stop_if_signaled、其他非零印一句放行;CI 步驟在 drift check 之後、continue-on-error 加 || true;兩檔與新增文字都不含連續字串「note-audit check」(grep 驗過),也不含 drift 的上線字串。
- 〈做法〉6:LUMOS_VERSION 升 v1.2、CHANGELOG 同版號一段(寫明 sonnet、codex 沒量過、只提醒不擋);skill 新增小節放在筆記內容審之後並含 prepare/record/提交;Systems/筆記內容審(說明與 about_code)、Systems/存量漂移守衛(掛鉤與 CI 那段補一句)、Systems/bound-tests-gate 都有改;anchor-baseline 在同一提交更新,在 94e28375 上 `lumos anchor verify` 通過;t_prepush_gates_stop_on_signal 期望值 5 改 6。_KNOWN_GATES、_VENDORED_TREE_FILES、_BOOKKEEPING_DIRS 三處都登記;repo 裡沒有其他寫死 note-verdicts 的清單需要同步(grep 驗過)。
- 條款測試:S1–S9、S11–S14 各一支都在且名稱與計劃一致;在 94e28375 上跑 `-k reread`:88 passed, 0 failed。S10 數字已記進〈實作紀錄〉(真漂移 15,過門檻 14)。

〈實作紀錄〉列的偏離,站得住:刪除分支記 none(〈做法〉4 與 S7 字面自相矛盾,取後者合理,測試也照 none 驗)、reasons 帶種類、{{NOTE}} 填圖譜內相對路徑、兩樣附加放在輸出格式之後、record 不重算指紋、零點出行也寫紀錄、開關在範圍解析之前讀、ls-tree 帶結尾斜線、-M 明寫。實跑沒有看到它們造成錯的行為。

未列入〈實作紀錄〉但不構成不同行為的小差異(不標 finding):
- reread-check 的提醒多印一行「其中 N 篇在工作目錄有對照紀錄、還沒提交」(只是提示,紀錄沒提交照樣被列、符合 S6)。
- 逾時的 skipped 原因寫「逾時(超過 30 秒)」,計劃寫「原因 timeout」;S7 只要求印原因並記一筆 skipped,語意一致。
- reread-prepare 印的是每份項目檔的路徑加一段共用派法,不是每份各一行完整派工指令。

最高等級:clean
