severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/f3b14b9013b101f76c2efb2ba10e03590b7dee804dac886ccf600f7294b81792.json.warming` 不存在,我沒碰任何鎖,直接照派工詞審查。

## 問 1:分層與依賴方向

結論:結構對齊,沒有跨層直呼。有一處讀取方式不一致,見 B2。

- **掛鉤端:** 新增的重查指令放在 `pp_record_block` 的第 4 個參數。它跟既有的旗標與筆數一樣存成記憶體純量 `_PP_FIRST_NEXT`,不寫進 `blocks` 暫存檔,三欄格式不變,`push-summary` 與 `pp_plain_summary` 的讀法沒動。
  - 對照 `scripts/hooks/pre-push:106-117`:純量不用陣列(bash 3.2 搭 set -u 的註解)。
  - 最後一行由掛鉤自己印,不經 lumos,所以呼叫方向沒變:閘 → `pp_record_block` → 判斷點。
  - 所有 15 個 `pp_record_block` 呼叫點都補了第 4 參數,沒有遺漏。
  - 全套測試紅與自主迴圈紅這兩條不經彙總的路,就地 `echo` 後 `exit 1`,跟它們原本的寫法一致。
- **`scripts/lumos` 端:** 作廢過濾放進唯一掃描 `_contract_key_matches`,對照該函式 docstring 的「全檔唯一的合約行掃描」,層次正確。
- **測試端:** 新增的 `_ppc_last_line`、`_ppc_call_tokens`、`_ppc_next_matches_call` 與 `_PPC_NEXT_DROP` 沿用 `_ppc_*`、`_PPC_*` 命名,呼叫的是 `_ppc_run`、`_ppc_repo`、`_ppc_cleanup`、`_nh_git`、`_need_src`、`GRAPHCTL`,跟 `scripts/test_lumos.py:82165-82264` 的同層做法一樣。

引句:「  [[ -z "$_PP_FIRST_NEXT" ]] || echo "下一步:$_PP_FIRST_NEXT" >&2」

## 問 2:命名與錯誤處理

結論:掛鉤與測試都對齊,`scripts/lumos` 有一條 minor(B1)。

- **掛鉤:** `_PP_FIRST_NEXT` 沿用 `_PP_BLOCKED`、`_PP_NBLK` 的全域前綴。`_cl_next`、`_push_args` 是迴圈內的小寫區域變數,跟 `_cl_out`、`_cl_bl`、`_hrange` 同族。可選參數用 `${4:-}`,跟既有的 `${...:-}` 一致。第一個擋下的閘沒給指令就不印那行,不會遞補別道的指令,這跟「記下不改擋不擋」的原則一致。
- **測試:** 新測試沿用 `print("t_…")`、`check(…)` 與 `try/finally: _ppc_cleanup`,函式內 `import subprocess as sp` 也跟鄰居一樣(全檔 186 處)。`t_superseded_contract_not_sent` 沒帶區域前綴,但同檔已有 `t_superseded_note_revisits_listed_and_marked`,不算不一致。

引句:「  [[ "$_PP_NBLK" -gt 1 ]] || _PP_FIRST_NEXT="${4:-}"」

### B1:`_ns_superseded` 三個新呼叫點,傳入的字串三種形狀

severity: minor
blocking: no

`_ns_superseded` 的 docstring(`scripts/lumos:4847` 的 `slot_parse`)寫的是「前綴冒號後面的字」。既有呼叫點傳「冒號後面」的字串,例如 `scripts/lumos:4488` 的 `_ns_superseded(rest)`、`scripts/lumos:50323` 的 `_ns_superseded(s[len(m.group(1)) + 1:])`、`scripts/lumos:51981` 的 `_ns_superseded(line[len("RULE:"):])`。唯一例外是 `scripts/lumos:46071`,傳整行。

這份 diff 在三個新呼叫點用了三種寫法:

- 傳 `extract_contracts` 回來、已去掉 `KEY:` 與標記的字串 `x`。
- 傳含 `KEY:` 的整行 `line`。
- 傳 `s.partition(":")[2]`。

`slot_parse` 只掃 `[鍵:值]` 欄位,所以行為上等價,結構沒壞。但同一個意圖有三種寫法,後人要猜哪個才是慣例。

引句:「invs = [x for x in invs if not _ns_superseded(x)]」
引句:「if IRREVERSIBLE_RE.match(line.strip()) and not _ns_superseded(line):」
引句:「if not _ns_superseded(s.partition(":")[2]):」

## 問 3:第二種做法

結論:沒有引入掛鉤端的第二種做法,有一條 minor 的疑點(B2),交編排者定奪。

- **引號處理:**
  - 掛鉤裡給人照抄的指令,既有做法是寫死的字串,例如 `lumos anchor approve --note "為什麼改"`,以及 `$PY scripts/test_lumos.py --ff -x`。
  - 新增的指令帶了變數(分支名、遠端名、ref 名),用 `printf '%q'` 處理,這是 `scripts/hooks/` 內第一次出現。
  - 專案在 lumos 端本來就靠 `shlex.quote`(`scripts/lumos` 28 處),`%q` 是 bash 對應的標準寫法,掛鉤裡也沒有現成的引號工具函式可重用,所以不算自創第二套。
  - 測試 ③ 把印出的那行貼進真的 `/bin/bash` 執行,驗證分號不會斷開指令。
- **陣列展開:** `${_ba+ ${_ba[*]}}` 與既有的 `${_ba+"${_ba[@]}"}`(`scripts/hooks/pre-push:584`)用的是同一個 `+` 判空守則(對 bash 3.2 與 set -u 安全),只是為了接成字串改用 `[*]`,不算新做法。
- **重查指令的內容:** 各閘都是它當下實際跑的那一條,只去掉 `--repo` 與暫存檔旗標,沿用既有的使用者可見用詞 `lumos …`,而不是 `$PY $GRAPHCTL`。測試端的 `$PY scripts/test_*.py` 也跟原本 `scripts/hooks/pre-push:459` 的寫法一致。

引句:「_push_args="--push-remote $(printf '%q' "$_PP_REMOTE") --pushed-ref $(printf '%q' "$_rref")"」

### B2:`_impact_contract` 在呼叫端自己再濾一次,跟「全檔唯一掃描」的原則有張力 ⚠

severity: minor
blocking: no

- **原則:** `_contract_key_matches` 的 docstring 與 `scripts/lumos:64671` 的註解都寫著「別再各寫一份」,要求合約行的判法只有一份。
- **這份 diff 的做法:** 作廢過濾在 `_contract_key_matches` 做一次,又在 `_impact_contract` 對 `extract_contracts` 的結果與 `IRREVERSIBLE_RE` 的比對各手寫一次。
- **為什麼沒判 major:**
  - `_impact_contract` 本來就走 `extract_contracts` 加獨立的 `IRREVERSIBLE_RE`,不走 `_contract_key_matches`,所以「兩條讀取路徑」是既有的,不是這份 diff 新開。
  - 派工鏡頭筆記已寫明不改 `extract_contracts` 的理由(`doctor` 等二十幾處呼叫靠它查合約帳)。
  - 沒有新工具函式,只是在既有路徑各補一行。
- **要交編排者判的地方:** 作廢的定義現在散在兩處,而且 doctor 等其他 `extract_contracts` 使用者仍把作廢行算進去。這個缺口筆記已承認並留給另案,所以我只標 minor。

引句:「invs = [x for x in invs if not _ns_superseded(x)]」

不對齊共 2 條,其中 major 0 條
