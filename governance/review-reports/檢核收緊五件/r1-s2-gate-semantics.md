# r1-s2 閘語意與合取正確性審查——S2 棘輪 / S3 外家 fail-closed

審查對象:`/tmp/檢核收緊五件-r1.md`(S2 軟提醒棘輪、S3 外家席缺席 fail-closed)。
方法:逐條規則對照真實 code(`scripts/lumos`,~15,100 行)與真實資料(`governance/review-reports/**/*dispatch*.json` 82 個檔案),找「照字面實作 → 閘判定結果錯」的輸入。

---

## Finding 1(blocker):`ratchet_ack` 走 scalar `lumos set`,同節點兩道閘會互相清除逃生痕

引句：「節點 frontmatter `ratchet_ack: <gate>@<date>`(走 `lumos set`,白名單加一鍵)」

**問題**:文件把逃生欄位定成「白名單加一鍵」,即比照 `scripts/lumos:7039` 的 `SCALAR_KEYS`(`{"status","updated","created","type","self_audit","signed_off","regen","pitfall_ask","pitfall_source"}`)模式——單一純量,`cmd_set`(`scripts/lumos:7300-7326`)用 `edit_fm_scalar` **整欄覆寫**,同 key 只留最後一次寫入的值(`self_audit: <model>/<date>` 正是同款慣例,見 `scripts/lumos:7330-7344`)。

但同一節點完全可能被**兩個不同 gate** 同時棘輪升級(例如同一節點在 check-s 與 check-r 都各自累積 ≥20 commit)。`ratchet_ack` 若設計成「一欄存一組 `<gate>@<date>`」,人對 gate A 執行 `lumos set X ratchet_ack check-s@2026-08-21` 之後,若又對 gate B 執行 `lumos set X ratchet_ack check-r@2026-08-25`,第二次寫入會**整欄覆寫**、悄悄抹掉對 check-s 的 ack——check-s 的 30 天窗口消失,下次 `doctor --ci` 該節點在 check-s 這道閘會**無預警恢復硬擋**,即使人以為自己已經 ack 過。這正是「逃生口留痕」設計初衷要防的反面(讓 gate FAIL 看起來像是無理由復發)。

**正確規則**:`ratchet_ack` 若要支援多 gate 同節點併存,不能走 `SCALAR_KEYS` 單值覆寫模式——需要 list 語意(走 `LIST_KEYS`/`append` 白名單,`scripts/lumos:7347-7358`)或改成 `ratchet_ack_<gate>` 分欄,並在文件裡明講「同節點多 gate 各自一條 ack」。

---

## Finding 2(major):棘輪鍵只認節點 `stem`,而 `stem` 在本圖譜可碰撞

引句：「同一 (gate, node) 在 **≥20 個不同 commit** 出現、且末次出現在最近 7 天內(=仍在被念,非已停止)→ 該 (gate,node) 升級。」

**問題**:目前所有會寫入 `.governance-log.jsonl` 的軟提醒(ratchet 的唯一輸入源)一律只記**node stem**,不記完整路徑——`scripts/lumos:792`(check-r `nodes: [nnote.stem]`)、`819/825`(check-s)、`866`(check-e1)、`948`(check-e2)、`989`(check-e3)、`1030`(check-k)、`1307`(check-j),寫法全同。而本圖譜本身就結構性地承認 stem 會碰撞——`scripts/lumos:478` 的 `collisions = {s: rs for s, rs in by_stem.items() if len(rs) > 1}` 是 doctor 既有的一個檢查項,`by_stem`(`scripts/lumos:236-239`)索引全 vault 不分資料夾。

於是:兩個不同節點(例如 `Issues/foo` 與 `Projects/foo`,同 stem `foo`)若各自被同一 gate 分別警告 12 次與 10 次(單獨都未達 20),棘輪讀到的 `.governance-log.jsonl` 只看得到 stem="foo" 出現在 22 個不同 commit——**合併成一個 (gate,foo) 命中並升級**,對兩個各自都還沒到門檻的節點都錯誤地硬擋。逃生門也隨之壞掉:人對其中一個 `foo` 節點 `lumos set foo ratchet_ack ...`,ack 寫在哪個實體檔?ratchet 讀帳時只有 stem 字串,無法判斷這次升級到底該歸給哪個物理節點,ack 也就對不上。

**正確規則**:棘輪的鍵至少要能還原到唯一節點(存完整 rel path,或在寫入時順帶把碰撞情形排除/標記),不能沿用現有「只記 stem」的寫法。

---

## Finding 3(major):現行只有 7 道 gate 真的寫 `.governance-log.jsonl`,棘輪結構上抓不到其餘軟提醒

引句：「既有 `docs/.governance-log.jsonl`,只看 `hard=false ∧ kind=warned` 的事件。」

**問題**:S2 的立案動機(Growth test 第①點)明講「check-s 軟提醒響 18,283 次/46 天零人處理」是本案要解的真事故,暗示棘輪要能接住「任何被長期無視的軟提醒」。但檢視 `run_doctor`(`scripts/lumos:446-1334`)全部 Check,實際會 `gov_events.append(...)` 寫進 `.governance-log.jsonl` 的只有 check-r(785/789/792)、check-s(819/825)、check-e1(866)、check-e2(948)、check-e3(989)、check-k(1030)、check-j(1307)共 7 道。Check H(漏標可逆性,`1002-1016`)、Check V(valid_under 過期,`1083-1101`)、Check P(失效檔案認領,`1103-1141`)、Check Y(符號存在性,`1168-1229`)、Check N(可重算數字,`1231-1290`)、Check D(紀律區塊漂移,`1045-1081`)全部只 `warn_soft`,**從未寫 gov_events**——這些提醒不管響幾次、放幾年沒人理,棘輪永遠讀不到,不可能升級。

**正確規則**:若棘輪的承諾是「軟提醒被無視 N 次就升級」,輸入源不能限定「既有 `.governance-log.jsonl`」——要嘛把 Check H/V/P/Y/N/D 也接進 gov_events(等於是本案隱藏的第六個子任務,不在「零新子命令、既有指令讀側加段」的範圍刀內),要嘛在文件裡明講棘輪的覆蓋範圍只有 7/13 道 Check,別讓人以為「所有軟提醒最終都會被棘輪接住」。

---

## Finding 4(blocker):`tier=high` 判準依賴的 `tier` 是選填欄,`loop status` 根本沒有 `--tier` 旗標

引句：「`loop status --panel --gate` 對 **kind=code ∧ tier=high** 的 loop(kind 依 loop id 前綴三值規則,同派工編制案)」

**問題**:`loop status` 的 argparse(`scripts/lumos:14291-14311`)完全沒有 `--tier` 參數。全 repo 唯一取得某 loop tier 的方式是「帳面首個帶 tier 記錄定錨」(`cmd_loop_next` 的 `scripts/lumos:4824-4829` 邏輯:`anchor = next((r["tier"] for r in rounds if r.get("tier")), None)`)——即讀 `.canary-log.jsonl` 裡任何一輪 `canary record --tier high` 是否曾經被打過。而 `canary record` 的 `--tier`(`scripts/lumos:14277-14278`)本身是**選填**(`choices=(...)` 但無 `required=True`),`_roster_observe`(`scripts/lumos:4701-4705`)甚至把「未帶 tier」印成「無定錨」並直接跳過對帳,可見這是常態、不是異常。

換言之:一個真正屬於 code/high 的 loop,只要編排者(人)在每輪 `canary record` 時忘了(或懶得)加 `--tier high`,`_loop_status_panel` 讀到的 rounds 裡沒有任何一輪帶 tier 欄——S3 判準「kind=code ∧ tier=high」永遠比對不上,**外家 fail-closed 完全不會觸發**,悄悄退回成「轉述、不執行」——正是本案自己想從 v1 升級掉的那個狀態。這是本案的核心賣點(`_TIER_ROSTER` 的 `required-fail-closed` 從轉述變執行)被一個選填欄位直接繞過。

**正確規則**:要嘛把 `--tier` 在 code/high 場景改成強制(至少對 `code-` 前綴 loop 的首輪 record 強制要求),要嘛 S3 判準本身要對「tier 未定錨」的 code loop 定義明確的 fail-closed 缺省(例如:kind=code 且從未定錨 tier 時,不能預設「非 high」而放行,應反過來預設「未知就當高風險擋」,否則整條規則名不符實)。

---

## Finding 5(major):`跨 loop 累計...依 ts 排序`——dispatch 檔案的真實 schema 裡沒有 `ts` 欄

引句：「不擋;`loop next` 印「外家席連續 N 輪缺席」(跨 loop 累計,讀全部 dispatch 依 ts 排序)」

**問題**:實測全 repo 現存 dispatch 檔:

```
$ find governance/review-reports -iname "*dispatch*.json" | wc -l
82
$ find governance/review-reports -iname "*dispatch*.json" | xargs grep -l '"ts"' | wc -l
0
```

例如剛產生的 `governance/review-reports/檢核收緊五件/r1-dispatch-s2-gate-semantics.json`:
`{"round":"r1","seat":"s2-gate-semantics","lens":"...","materials":[...],"auditor":"s2-gate-semantics-sonnet"}`——欄位只有 `round`/`seat`/`lens`/`materials`/`auditor`(或 `seats`/`canary`),`_roster_dispatch_entries`(`scripts/lumos:4666-4691`)記載的三種真實形狀也都沒有 `ts`。82 個真實檔案 0 個帶 `ts`。

「跨 loop 累計、依 ts 排序」這條規則在真資料上沒有欄位可排——照字面實作只有兩條路:(a) 對缺 `ts` 的檔案拋錯/跳過,結果 streak 計數系統性漏掉所有現存 loop;(b) 退而求其次用檔案 mtime 代替(文件未提、且 mtime 會因 checkout/複製/rebase 而改變,不是可靠的時序代理)。兩條路都會讓「外家席連續 N 輪缺席」這條 streak 判斷算錯。

**正確規則**:要嘛在 dispatch schema 補一個真正的 `ts` 欄(等於是本案隱藏的 schema 變更,牴觸「零新資料結構」的框定),要嘛改用真正存在、單調的鍵排序(例如 round-id 內數字序 + loop 目錄底下檔案 glob 序,但要接受「跨 loop」比較本來就沒有全域時序這個事實,別再寫「依 ts 排序」)。

---

## Finding 6(major):`--gate` 在 `--panel` 模式下是既有的 no-op,不是「加了才生效」的開關

引句：「`loop status --panel --gate` 對 **kind=code ∧ tier=high** 的 loop」

**問題**:`cmd_loop_status`(`scripts/lumos:4415-4420`)在 `panel` 分支完全不傳 `gate` 參數:

```python
if panel:
    try:
        return _loop_status_panel(rounds, loop_id, min_seats=min_seats, spec=spec)
```

`_loop_status_panel` 的簽名(`scripts/lumos:3638`)本來就沒有 `gate` 形參。而且這不是遺漏——CLI help 自己白紙黑字寫死了這個慣例(`scripts/lumos:14300-14301`,`--panel` 的 help text):「`--gate` 對 panel 為相容 no-op(panel 判準恆生效)」。也就是說 panel 模式下所有既有合取(輪有效/存活/G3 hash/…)**不分有沒有 `--gate` 一律生效**,`--gate` 純粹是相容擺飾。

文件用「`loop status --panel --gate`」這個寫法暗示外家 fail-closed 是「加了 `--gate` 才會擋」,但若照 panel 既有慣例實作(即所有 panel 合取恆生效),S3 的外家檢查會對**任何** `loop status --panel`(不管有沒有帶 `--gate`)都生效——包括單純想看進度、沒打算做收斂判定的呼叫。這會讓既有腳本/hook 裡任何裸 `loop status --panel` 呼叫在外家缺席時意外收到 `⛔ PANEL GATE FAIL`,超出使用者原本的預期範圍。反過來,若為了讓「必須帶 `--gate` 才擋」成立而真的去幫 panel 路徑接上 `gate` 參數,那就是一次牴觸「零新子命令、既有指令讀側加段」框定的介面變更,測試矩陣(`t_external_failclosed_code_high`)也完全沒有涵蓋「帶 `--panel` 不帶 `--gate`」這個案例來釐清到底哪種語意才對。

**正確規則**:文件必須先講清楚 S3 是要對齊「panel 恆生效、`--gate` 是 no-op」的既有慣例,還是要為此新開一條「`--gate` 在 panel 下真的有作用」的例外——兩者行為天差地遠,而目前文件的措辭剛好卡在兩者中間、暗示了一個 code 裡不存在的條件式。

---

## Finding 7(major):`_roster_kind` 是前綴命名慣例、非結構保證,升級成硬擋後誤判代價從「講錯話」變成「fail-open」

引句：「kind 依 loop id 前綴三值規則,同派工編制案」

**問題**:`_roster_kind`(`scripts/lumos:4644-4651`)的判法是:`code-` 開頭 → `code`;`code` 開頭但無連字號 → `None`(indeterminate);其餘一律 → `design`。這個函式目前只餵給 `--roster` 這種 **advisory、恆 rc0**(`scripts/lumos:4392-4393` 的觀測段落,任何例外都只降級為警告)的對帳段落,誤判的代價僅止於印錯一行觀測文字。

S3 把同一個函式的判定結果直接拿去決定「要不要 fail-closed 硬擋」。因為 loop id 前綴純粹是**命名慣例**、repo 裡沒有任何機制強制「真正的 code/high review 一定要以 `code-` 開頭命名」,任何一個實際上是 code/high 審查、但被取名成不帶 `code-` 前綴(例如舊習慣沿用的 `檢核收緊五件` 這種中文專案名——本次審查自己所在的 loop 目錄 `governance/review-reports/檢核收緊五件/` 就是這種命名,`_roster_kind` 會把它判成 `design`)的 loop,會被整條規則判定成「design/high、standard、indeterminate」那一支——只印 streak、**不擋**。這正好是把一個本該 fail-closed 的高風險 code 審查,因為命名習慣而悄悄降回「轉述」等級,與本案想解決的「宣稱有守衛、實際沒有」是同一種失敗形態。

**正確規則**:把一個原本只餵 advisory 觀測的啟發式函式,原封不動升格成硬擋判準之前,至少要先確認「kind=code」判定本身有沒有結構性保證(例如要求 code/high loop 必須在某處顯式宣告 kind,而非只靠 id 前綴猜),否則命名習慣的誤差會直接轉譯成 fail-closed 的漏洞。

---

## 嚴重度統計

blocker: 3、major: 4、minor: 0
