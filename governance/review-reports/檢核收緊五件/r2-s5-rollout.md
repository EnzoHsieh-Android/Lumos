# r2 s5 — rollout order / blast radius / 退場條件 對抗審計

審材:`/tmp/檢核收緊五件-r2.md`(122 行)。鏡頭:rollout 順序、單一 PR 能否在自己的新規則下 commit/push、`gov --stats` 是否真能印出退場條件要的數。逐條核對 `scripts/lumos`(~15,100 行)與 `scripts/hooks/pre-commit`、`scripts/hooks/pre-push`、`scripts/test_lumos.py` 真碼 + 實跑 `gov --stats --since 90`。

---

## F1(blocker)——S3「range 同 pre-push」的宣稱不實,pass 的 tier 判定可能與真正放行點分歧

引句：「range 取 merge-base..HEAD,同 pre-push」

**錯在哪**:文件宣稱 `pass` 內自跑 pitfalls 判 tier 時「range 取 merge-base..HEAD,同 pre-push」——但 pre-push 實際算的 range **不是** merge-base..HEAD。

`scripts/hooks/pre-push:85-94`:
```
_range=""
if [[ "$_rsha" == "$_ZERO" ]]; then
  _range="$_EMPTY_TREE..$_lsha"      # 新 ref
elif ! git cat-file -e "$_rsha" 2>/dev/null; then
  _range="$_EMPTY_TREE..$_lsha"      # remote_sha 本地無此物件
else
  _range="$_rsha..$_lsha"            # 一般情形:增量 endpoint diff
fi
```
第 110 行呼叫 `code-loop check --diff "$_range" ...` 時**永遠帶 `--diff`**,不會落到 `_codeloop_guard_verdict` 的 merge-base 分支(scripts/lumos:14064-14078 那段 `if diff_range is None:` 的「現行為:merge-base..HEAD 推導」只在**沒傳 `--diff`** 時才跑,注解自己也寫「向後相容」,不是 pre-push 用的路徑)。

一般情形的 `$_rsha..$_lsha` 是「上次推到 remote 的 sha .. 這次要推的 sha」——對同一分支多次推送(最常見的迭代開發場景),這條範圍只涵蓋**這次新增的 commit**,與 merge-base..HEAD(**整條分支相對 main 的累積 diff**)在多次推送下幾乎必然不同。

**後果**:`pass --loop` 用 merge-base..HEAD 算出的 tier,可能與 pre-push 真正拿去卡 push 的 tier(用 `$_rsha..$_lsha`)不一致。危險方向是:`pass` 算出 tier=standard(因整條分支累積內容被稀釋、或本次新增內容單獨判高但被歷史內容拉低)→ 不要求 `--loop`/`--no-loop`,直接無條件寫 `status: passed`(`scripts/lumos:14168-14176`,這段完全沒有 tier 判斷,純寫入);之後 pre-push 用 `_codeloop_guard_verdict` 讀到「有效留痕(passed)」就放行(scripts/lumos:14101-14107)——**外家 fail-closed 從未被驗證過,却順利通過**。這正是 r1 s4-F3 blocker 想解決的「閘可繞」問題,本次修法只是換了一個新的分歧點,不是真的「綁在放行點」。

**正確做法**:`pass` 判 tier 時應該重用 pre-push 同一套 range 推導邏輯(讀 stdin 推送範圍 / 或至少要求呼叫者用 `--diff` 明確傳入即將推送的 range,而非 pass 自己另外推導 merge-base..HEAD),否則兩處各算各的,parity 只是口頭宣稱。

---

## F2(blocker)——S3 退場條件的分母「code-loop(passed)筆數」無法從 `gov --stats` 該表讀出

引句：「`external-waived` 筆數 vs `code-loop`(passed)筆數」

**錯在哪**:`gov --stats` 的彙整表按 `gate` 分組,不分 `kind`。`_render_gov_stats`(scripts/lumos:2909-2954)第 2924 行:
```python
a = agg.setdefault(r["gate"], {"raw": 0, "ded": 0, "nodes": set(), "commits": set(), "dates": set()})
```
只用 `r["gate"]` 當 key,`kind`(passed/skipped)完全沒有進聚合維度,印出來的表只有一行 `code-loop`,是 passed+skipped 的合計,不是「code-loop(passed)」單獨的數。

實跑證實:
```
$ python3 scripts/lumos gov --stats --since 90
...
  code-loop               79        79             n/a            79  2026-07-05 2026-08-21
```
再拆開原始帳驗證:
```
$ grep '"gate": "code-loop"' docs/.governance-log.jsonl | python3 -c "...Counter..."
Counter({'passed': 56, 'skipped': 23})
```
79 = 56(passed) + 23(skipped),表裡那一行**兩種都混在一起**,人拿這張表沒辦法直接讀出「passed 筆數」,得回頭手動 grep+過濾 kind——這正是 `gov --stats` 這功能(commit 訊息:「每道閘的純數字報表」)想取代掉的動作。文件在同段落自己主張「三件的分子分母**全部是已寫帳或本案新寫帳的 gate**,`gov --stats` 現有欄位即可印(★v1……v2 對三件逐條成立★)」——對 S3 這一列不成立,是偽陽性宣稱。

**正確做法**:要嘛 `_render_gov_stats` 加一層 (gate, kind) 分桶,要嘛退場條件改寫成明講「另跑 `gov --full` 過濾 kind=passed 手數」,不能宣稱「現有欄位即可印」。

---

## F3(major)——S2 退場條件「ack/升級 ≥50%」的分子分母尺度不可比

引句：「ack/升級 ≥50% → 門檻 20 重議」

**錯在哪**:`ratchet`(promoted)與 `ratchet-ack` 兩種事件的**發生頻率結構完全不同**,直接相除不代表「有多少比例被人接手處理」。

依 S2 設計原文(同文件 §S2「升級落帳」):「`--ci` 時每項寫 `gate: ratchet, kind: promoted`」——這是**每次 `--ci` 執行**、對**每一個仍在棘輪狀態的項目**都寫一筆,沒有任何去重/僅首次寫入的敘述。而 `.github/workflows/ci.yml` 是 `on: push` + `on: pull_request` 觸發,一個未解決的項目會在後續每次 push/CI 都重複計一次 `ratchet` promoted 事件。反觀 `ratchet-ack`:一次 `lumos append` 動作寫一筆,之後 30 天完全靜默,不會重複寫。分子(ack)是「動作次數」,分母(promoted)卻是「項目數 × 其間 CI 執行次數」的乘積——單位不同。

有實測可佐證同構的既有閘:`ratchet` 的輸入來源之一(`hard=false ∧ kind=warned`)就包含 `check-s`;`gov --stats` 實跑:
```
check-s               7407     18583              42           424  2026-07-02 2026-08-21
```
近 90 天 42 個不同節點,卻累積 7407 筆(去重後)/424 個不同 commit——平均每個 commit 就重複噴出 ~17.5 筆同類警告。若 `ratchet` 沿用同一種「每次跑就對仍卡住的項目再記一筆」模式(spec 文字看不出有例外),分母會被 CI 執行頻率灌得遠大於分子,使「ack/升級 ≥50%」這個重議觸發條件在實務上幾乎打不到,不管真實的人工處理率高不高——這條退場/重議判準等於是死的。

**正確做法**:分母改成「相異 (gate,節點) 的 ratchet 首次促升事件數」(去重到項目層級,而非每輪重複計),或直接明講「本判準以項目數而非事件筆數計」並補一條 dedup 規則。

---

## F4(major)——S3 沒有「本 PR 自己怎麼過自己新規則」的上線段,S1/S2 都有

引句：「真正擋 push 的是 `code-loop pass/skip` 留痕,不是 `loop status`」

**錯在哪**:S1 有「存量」段(先實掃詞表、逐條分型補標,才不會一上線就把既有 28~51 句全炸出來);S2 有「上線基線」段(明講 check-e1 現有 5 組會立刻升級,「上線 PR 必須先把這 5 組解掉或 ack,不得帶著紅上線」)。S3 沒有對應段落。

但 S3 恰恰是三件裡唯一會**卡住自己這次要提交的 PR** 的一件:實作 S1/S2/S3 的這個 PR 本身改動 `scripts/lumos` 多處(新詞表常數、doctor 一段、`_TIER_ROSTER`/`code-loop pass` 前置判定……),依現有 `_TIER_ROSTER[("code","high")]`(scripts/lumos:4633-4640)幾乎必為 tier=high。而 `pass --loop <id>` 落地後,這個 PR 自己 push 前就要滿足「最近 min(K=2,輪數) 輪中至少一輪 external 席數 ≥2(外家finder+外家否決)」,否則要用 `--no-loop`/`--waive-external` 才能留痕。

翻真實歷史帳:`governance/code-loop/*.json` 現有 6 筆 pass/skip 紀錄裡,`code-loop check`(pre-push 實際判定,`_codeloop_guard_verdict`,scripts/lumos:14046-14135)從來沒有檢查過席位組成——它只認「sha 匹配 + status ∈ {passed,skipped}」就放行(scripts/lumos:14101-14107)。也就是說**現存所有 code-loop pass 紀錄沒有一筆是在「2 席外家 fail-closed」規則下產生的**;新規則第一次真正被套用,就是套在這個 PR 自己身上。近期 code-loop 風格的專案(`governance/review-reports/code-標註刷新/r1-dispatch.json`)雖然已有 `crossfamily-gemini-flash`/`veto-gemini-flash` 兩席,但也在 `deviation` 欄自陳「Codex 到期;外家僅 Gemini 一家,finder 席+否決席同家承擔=跨家族獨立性折損」——這正是文件自己「未決」段點名、尚未裁定的爭議(「兩席同家族算不算兩席」)。S3 段落完全沒提「本 PR 上線時打算走 `--loop`(靠這個有爭議的單一外家雙席)還是 `--waive-external`」,S1/S2 都替自己的首次上線鋪了路,S3 沒有,是不對稱的缺口。

**正確做法**:S3 補一段「上線」,比照 S1/S2 明講:本 PR 提交時,`code-loop pass` 打算走哪條路(`--loop` 用現有 gemini 單家雙席,或直接 `--waive-external` 留痕),並讓這個決定與「未決」段的爭議顯式掛鉤,不要留白。

---

## F5(major)——S1 自己的退場條件寫了一句教科書等級的「靠自律」,卻不會被 Check A 自己的詞表抓到

引句：「每 90 天人工盤點一次」

**錯在哪**:S1 退場條件承認「漏抓無法自動量測(負事件)」,對策是「改為每 90 天人工盤點一次寫 Verification」——這是**沒有任何機械提醒/機械驗證「上次盤點是不是在 90 天內」的純人工週期任務**,本質就是 Check A 整套機制想抓的那類東西(有守衛的宣稱、實際上守衛是「人記得做」)。

但套 Check A 自己的詞表(`_RISK_ADMIT_LEXICON`:`靠自律`/`honor-system`/`無機械守衛`/`零檢查`/`零實作`;`純靠`/`不驗` 需同行有 `工具|code|程式|機制`)去掃「改為每 90 天人工盤點一次寫 Verification」這句——**一個詞都不命中**。這句話沒用到任何一個觸發詞,純粹描述「靠人週期性做一件事」,語意上跟「靠自律」是同一件事,卻因為是 keyword-based 掃描而不是語意判斷,逃過自己這道閘。文件裡也沒有替這句話標 `<!--lumos:risk=...-->` 標記。

這不是隨便找的邊角案例——這是**文件本身、就在定義 S1 收斂判準的那一行**,而且是三件「硬擋」機制之一自己的退場條件。如果連設計者寫這份 spec 時都沒把它標型,可以預期未來其他人寫類似的「先手動、之後再機械化」措辭時,Check A 一樣抓不到,而 Check A 存在的理由(2026-08-21 L4 清帳抓到「pass --note 須含效能答案」「probe 三參數」兩處 skill 寫「須」而 code 零檢查)講的就是「宣稱有守衛、實際沒有」——這句話正是同款。

**正確做法**:要嘛把這句改成有機械掛勾的形式(例如:doctor 印一則「距上次盤點 Verification 已 N 天」的 advisory 提醒,N>90 時喊),要嘛老實承認這是 risk=A(天花板)並標記,不要留白句逃過自己家的閘。

---

## F6(major)——`_KNOWN_GATES` 遷移只講了一半,漏了 `t_gov_stats_gate_drift` 的第二道釘

**錯在哪**(此條無單一可引句子,依「引句」硬性規定,改綁最貼近的敘述行):

引句：「`lumos lint` rc1;`doctor --ci` 計 issues;純 doctor 列不計。」

——雖然這句話字面在講 S1 硬度,但實際問題出在文件「遷移」段對 5 個新 gate literal 的落地方式交代不全,而該段落與此句同屬「怎麼把新東西掛進既有骨架」的敘述脈絡,是本項發現的最近錨點。

`scripts/test_lumos.py:3047-3061` 的 `t_gov_stats_gate_drift` 有兩道斷言,不是只有「`_KNOWN_GATES` 要含新 gate」這一道:
```python
lits = set(_re.findall(r'"gate": "([a-zA-Z0-9_-]+)"', src))
check("stats: 原始碼 gate 字面值全在 _KNOWN_GATES", lits and lits <= set(m), ...)
dyn = _re.findall(r'"gate": [^"]', src)
check("stats: 動態 gate 寫點恰為 1 處(讀側 passthrough)", len(dyn) == 1, ...)
```
第二道斷言要求全檔「`"gate":` 後面接的不是字串字面值」的位置**恰好 1 處**(現況是 `cmd_gov` 讀側的 `"gate": d.get("gate", "?")` passthrough,scripts/lumos:2989 一帶)。

文件「遷移」段只寫:「`_KNOWN_GATES` +5、`LIST_KEYS` +1、`_STATS_NODE_SEMANTICS` +1,皆有漂移測試釘」——完全沒提第二道「動態寫點恰 1 處」的釘。這件事之所以不是空穴來風:文件在 S1 段自己主張「雙入口抄 `check_regen_provenance()`」,整份文件的施工哲學是「共用既有骨架、別重造」;5 個新 gate(check-a/ratchet/ratchet-ack/external-waived/external-absent)若照這個哲學合理地收斂成一個共用的「寫治理帳」helper(參數化 `gate` 名),helper 內部勢必得寫成 `{"gate": gate, ...}`(變數,非字面值)——一旦落地,`dyn` 會從 1 變 2,直接把既有這道釘打紅。反過來,如果為了不打紅這道既有釘而堅持 5 處各自硬寫字面值字典(不共用 helper),又和文件自己倡導的「別重造、抄既有骨架」哲學衝突。文件的「遷移」段和「測試策略」段(22 條測試清單)都沒有一條測到這個既有釘、也沒有講清楚要選哪條路。

**正確做法**:遷移段補一句:5 個新 gate 的寫入點要嘛全部字面值(不搶用共用 helper 的 `gate` 參數化寫法),要嘛連帶更新 `t_gov_stats_gate_drift` 的 `len(dyn) == 1` 為 `== 2` 並說明新增的那個動態寫點是什麼——兩條路二選一,現在是沒選。

---

## F7(minor)——「Check A 硬度=`lumos lint` rc1」在目前的 hook 鏈裡不是自動觸發的

引句：「`lumos lint` rc1;`doctor --ci` 計 issues」

**現況**:`scripts/hooks/pre-commit` 全文(已讀完)完全沒有呼叫 `lumos lint` 或 `scripts/lumos lint`——它只做圖譜同步檢查(code 檔 staged 但沒有圖譜 .md 一起 staged 就擋),不驗內容。`lumos lint`(scripts/lumos:14232,「寫完一個節點立刻自驗」)是 CLAUDE.md 裡描述的**寫作者自律動作**(「寫完節點 `lumos lint <節點>` 自驗」),不是任何 git hook 自動跑的東西。真正機械擋下的時機只有 `doctor --ci`,落在 pre-push(可 `--no-verify` 略過)與 CI(push 後、不可略過)。

這不算文件邏輯錯(其餘既有閘,如 Check J,也是同一種「lint 手動快檢 + doctor --ci 硬擋」雙軌,文件說「雙入口抄 `check_regen_provenance()`」,行為上就是照抄這個既有慣例),但文件把「硬度」三個字用在 lint 上會讓人誤以為 commit 當下就會被攔——實際上 Check A 命中的最早自動攔截點是 push 時,不是 commit 時。既然本文件的整個立案動機是「檢核收緊」,值得在「硬度」段明講這個時間差(commit 可漏網、push 才真正擋),而不是讓「硬度」一詞造成誤解。

---

## 統計

7 findings:2 blocker / 4 major / 1 minor。
