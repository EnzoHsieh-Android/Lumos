severity: major

我把新檢查照字面插進 `_spec_gate_front` 的位置,在臨時 repo 實跑。臨時目錄與我自己留下的測試現場都已刪掉。沒改 repo。

**實跑結果**
- 插入點本身可行。零條款、風險低、`--no-run`、複製舊計劃四種都拿得到 `env`、`rel`、`text`、`rr`,前面的 `_spec_gate_pending` 沒有提早 return。
- 新計劃 A、B 在 `LUMOS_PLAN_SOURCES_SINCE` 為 2026-11-07 時被擋(rc=1)。
- 舊計劃 C(created 2026-10-01)只印提醒。
- 複製舊計劃(created 舊、第一次進 git 是 2026-11-06,生效日設 2026-11-06)判成新計劃,被擋。
- 補充:A(零條款、風險低)現在就被 `_spec_gate_clause_part` 的「風險低零條款一律擋」擋下。新檢查插在它前面,只是讓使用者先看到「缺〈依據來源〉」。
- 型錄計數照計劃的指令重跑,主表 473、有查證 140、出處不全 29、還沒逐列查證 324,全部相符。
- `lumos doctor` 全跑約 100 秒,結果是 0 issues、rc=0,提醒不影響判定,成本不是問題。todo 或 doing 的計劃有 185 篇,其中 184 篇沒有〈依據來源〉節。

### F1
引句:「測試總檔開頭同樣預設成 9999-12-31,讓既有規格閘測試停在生效前」
severity: major
blocking: 是
- 這個預設擋不住「讀不到日期當新計劃」。計劃的「兩個都讀不到當新計劃」會讓 `day=None` 判成新,不看生效日。
- 既有測試的計劃常常不帶 `created`,又是 `git commit` 之後才寫的(未追蹤),就會讀不到日期。
- 實驗:在臨時副本加上 `_PLAN_SOURCES_SINCE`、`_spec_gate_sources_part` 與測試總檔的 9999-12-31 預設,再跑 `python3.14 scripts/test_lumos.py -k spec_gate_expected`。
- 輸出:`[spec-gate] 依據來源: PROTO day=None since=9999-12-31 old=False has=False` 接著 `✗ 缺〈依據來源〉`,`t_spec_gate_expected_table_high` 2 條斷言紅(2 passed, 2 failed)。
- 該測試的 fixture 是 `_hre_repo` 寫的計劃(`file: scripts/test_lumos.py:74851`),此類 fixture 在測試檔裡約有 12 處。
- 全套 `-k spec_gate` 我沒跑完,所以不知道總共紅幾支。
- 預期值表的 `_expected_requirement` 沒踩這個洞,因為它另有 `_hre_since` 裝飾器逐測試覆寫(`file: scripts/lumos:14296`)。
- 照字面實作,既有規格閘測試會大量誤紅,計劃要補 fixture 全帶 `created`,或「讀不到日期」在測試總開關下判成舊。

### F2
引句:「回傳那幾列主表列來源欄的網址清單;對應檢查欄沒有主表編號 應 回空清單」
severity: major
blocking: 是
- S4 的範例 D-1 對不上現況。D-1 的對應檢查是 API-1、API-3、API-14,三列的來源欄都沒有網址、也沒有 `〔查證`,都在那 324 列還沒查證的裡面。
- 實查來源欄:API-1 是 `PLAN;REACT-DOCTOR;VERCEL;SC〔併:API-1、研C補〕`,API-3、API-14 同樣沒有網址。
- 照字面實作,D-1 回空清單。預期值表那列「D-1 → 三列來源欄的網址清單」做不出來。
- 決策表共 56 列,對應檢查全查不到任何網址的有 25 列,約 45% 的盲判候選拿不到出處。
- 這跟範圍 5 要的「盲判材料附出處」目的衝突。
- 計劃需要改 S4 的範例,或明說空清單是常態並規定盲判材料怎麼標示。

### F3
引句:「`lumos doctor` 數出狀態是 todo 或 doing、沒有〈依據來源〉節或節裡有缺出處列的計劃,列名字(最多 20 篇)」
severity: minor
blocking: 否
- 這一條不看新舊,185 篇 todo 或 doing 計劃裡 184 篇會被列。
- doctor 每次永遠印同一批 20 篇加總數,補不完就清不掉。
- 它只是提醒、不改 rc,所以不阻擋;但 RETIRE-IF 也看不出實際有沒有人在補。
- 建議只列「新計劃」,或改成印總數加按更新日排序。

總結:最嚴重是 F1,生效日預設擋不住「讀不到日期當新計劃」,既有規格閘測試會誤紅,另有 F2 範例對不上型錄;會擋 2 條。
