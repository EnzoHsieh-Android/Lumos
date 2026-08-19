# 閘觸發帳統計 r2 — S1 對抗審計:implementability / definitional completeness

審查對象:`/tmp/閘觸發帳統計-r2.md`(154 行)。範圍限定:能否「無需再問一句」照字面把設計實作出來。已核對 round 1(審計修正紀錄)清單,以下不重複其已列項目,只報 round 1 遺漏或「宣稱已修但沒修完整」的洞。

---

## Blocker

### B1 — 漂移測試的掃描目標(`gov_events.append`)覆蓋不到七源母體裡至少 8 個真實 gate 名,「零觸發桶產不出來」的 blocker 只修了一半

引句：「`scripts/lumos` 內所有 `gov_events.append({"gate": ...})` 的字面值都在表內」

round 1 已把「需要 `_KNOWN_GATES` 全集」列為 blocker 並「已改」,但**沒有人去查這條漂移測試本身是否真的掃得到全集**——這正是本審查題目明講要驗的事,而 round 1 三席與編排者自查的十四條清單裡完全沒出現。

實測 `scripts/lumos` 全部 `"gate":` 字面值寫入點:

| gate | 寫入方式 | file:line | 是 `gov_events.append` 嗎 |
|---|---|---|---|
| check-r/check-s/check-e1/check-e2/check-e3/check-k/check-j | `gov_events.append({"gate": ...})` | 785,789,792,819,825,866,948,989,1030,1303 | ✅ 是 |
| check-j(shallow-skip 分支) | `gov.append({"gate": "check-j", ...})`(函式內部局部變數叫 `gov` 不叫 `gov_events`) | 2473 | ❌ 否(變數名不同,textual scan 抓不到,但此 gate 名已被上面 1303 涵蓋) |
| **anchor-approve** | `_append_governance_log(v, [{"gate": "anchor-approve", ...}])`——直接呼叫寫入函式,繞過 `gov_events` 這個 list 完全不經過 | 10071 | ❌ 否 |
| **code-loop** | `_codeloop_gov_log`:`with open(path,"a") as f: f.write(json.dumps(event...))`——連 `_append_governance_log` 都不經過,直接開檔寫 raw JSONL | 13940-13961(gate 字面值在 13956) | ❌ 否 |
| **L2**(bypass) | `cmd_gov` 自己的 `load(".bypass-log.jsonl", lambda d: {"gate": "L2", ...})` | 2911-2912 | ❌ 否 |
| **L3**(rot-queue) | 同上,`load(".rot-queue.jsonl", lambda d: {"gate": "L3", ...})` | 2913-2915 | ❌ 否 |
| **signoff** | `load(".signoff-log.jsonl", lambda d: {"gate": "signoff", ...})` | 2920-2923 | ❌ 否 |
| **kill** | `load(".kill-log.jsonl", lambda d: {"gate": "kill", ...})` | 2925-2930 | ❌ 否 |
| **canary** | `load(".canary-log.jsonl", lambda d: {"gate": "canary", ...})` | 2931-2939 | ❌ 否 |
| **ci** | `load(CI_LOG_NAME, lambda d: {"gate": "ci", ...})` | 2944-2947 | ❌ 否 |

即:S1 自己定義的「母體 = `lumos gov` 既有讀入的帳(bypass/rot-queue/governance/canary/kill/signoff/ci)」(第 56 行)裡,**7 源中的 6 源**(bypass/rot-queue/canary/kill/signoff/ci)的 gate 名是 `cmd_gov` 內 `load()` lambda 裡的字面值,根本不透過 `gov_events.append`;governance 這一源本身在讀側是 `"gate": d.get("gate", "?")`(2917 行,動態透傳,不是字面值),它的字面值要去寫側(doctor 的 `gov_events.append` + `anchor-approve` 的 `_append_governance_log` + `code-loop` 的 raw write)才找得到——三種完全不同的寫入路徑。

若把「掃描所有 `gov_events.append` 呼叫」照字面實作成測試,它只會抓到 7 個 doctor gate 名(check-r/s/e1/e2/e3/k/j),**完全抓不到 L2、L3、signoff、kill、canary、ci、anchor-approve、code-loop 這 8 個 gate 名**——而這 8 個恰好包含文件自己基線表(第 29-33 行)裡報數字的 `anchor-approve`(139 筆)、`code-loop`(77 筆),以及第 40 行明講「本來就把多本帳合流成同一組 gate 值」的 canary/kill/signoff。這條測試對這 8 個 gate 的漂移(改名、刪除、被移出表)**永遠不會翻紅**——與文件宣稱的「漂了機械翻紅」「零觸發桶的產生前提」直接矛盾:如果 `_KNOWN_GATES` 手動把這 8 個補進去,測試也驗證不了它們是否還對得上原始碼;如果漏了,測試更不會抓到。這不是「測項寫不完整」的 minor 問題,是**這條測試對母體過半的 gate 是啞的**,而它被文件定位成「頭號證據的產生前提,不是選配」——照字面實作出來的東西達不到文件宣稱的保證。

---

## Major

### M1 — 三條「輸出首行印 X」規則互斥,沒有排序規則,同時觸發時無法同時滿足

引句：「輸出首行印本次實際載入哪幾源」
引句：「輸出首行印「⚠ 已縮限至節點 <name>,以下統計僅為該節點視角」」
引句：「沿用,預設 90 天;輸出首行印實際窗口。」

第 56、99、101 行各自獨立宣稱「首行印 X」(load 源清單 / 節點縮限警示 / 實際窗口),三者的觸發條件互不排斥——例如 `lumos gov mynode --stats --since 30` 會同時符合「有節點位置參數」與「非預設 --since」,而 load 源清單規則(是否含 ci 源)幾乎每次都成立。三條規則字面上都要求「首行」(單數、第一行),但一次輸出只能有一個第一行。文件從未給排序(例如「依 A→B→C 順序印為前三行」),測試策略(#1/#8/#10)也各自獨立驗「首行有這行」,沒有一案驗證三者同時成立時的順序或共存,implementer 無法只憑文件把這三條規則同時落地成一致的輸出。

### M2 — `--stats` 帶入時,統計區塊相對既有 `gov` 輸出的印出位置(取代 / 附加在前 / 附加在後)完全未定義

引句：「不帶 `--stats` 時 `gov` 輸出**逐字元不變**(既有消費者零擾動),此為硬要求。」

這條(第 102 行)連同範圍刀第 110 行「不帶 `--stats` 時不改 `gov` 既有輸出」只鎖死了「不帶旗標」的那一半行為。文件通篇沒有一句話講「帶 `--stats` 時,原本的事件列表(呈現行,預設模式下約 1,026 行)還印不印、統計表放在它前面還後面、還是統計表完全取代原本列表」。這不是可以從既有慣例猜出來的:`gov` 預設模式本身已經有「呈現去噪」這層折疊(S1 已花一整段講三層數字不可混),`--stats` 究竟是「疊加一段」還是「換一種畫面」,決定了整個指令在 `--stats` 模式下的可讀性與既有腳本(若有人 parse `gov` 輸出)的相容性,測試 #9(`--full` 併用時統計段逐字元不變)、#11(`--stats` 恆 rc0)都只驗了統計段本身的內容,沒有一案釘死它和既有事件列表的相對位置或取代關係。

### M3 — 「首見日/末見日」兩欄在零觸發桶(該案例分類的頭號證據對象)下的印出值未定義,也未被任何測試覆蓋

引句：「**八欄**:去重後筆數、原始行數、不同節點數、不同 commit 數、首見日、末見日、收斂指標、分類桶。」

第 80 行定義八欄,收斂指標欄已明講「分母為 0 → 全欄 n/a」(第 85 行)的 fallback,但「首見日」「末見日」這兩欄是獨立欄位,不屬於收斂指標的「全欄 n/a」範圍——一個零觸發 gate(窗口內零筆,例如文件基線表本身列出的 `check-r`/`check-j`/`check-k`/`check-e2`/`check-e3`,現實已有五個實例)沒有任何一列可取「首次/末次出現日」,這兩欄該印什麼(空字串?`n/a`?不印該欄?)全文沒有一句話講。測試 #3(`t_gov_stats_known_gates`)只驗「表中零筆 gate 出現在零觸發桶且措辭含自曝限制句」,測項 #1(`t_gov_stats_fields`)只講「每 gate 八欄值正確」而未定義「正確」在零筆情況下是什麼值——沒有一條測試真正釘死這兩欄在零觸發情境下的輸出。這正好命中本案自己最強調、最先展示的頭號案例(五道 doctor 檢查零觸發),implementer 在寫第一個測試 fixture 時就會卡住。

---

## Minor

### m1 — 「本帳實見 `warned`/`blocked`/…」的事實陳述與文件自己的基線表互相矛盾

引句：「本帳實見 `warned`/`blocked`/`approved`/`passed`/`skipped`」

實測 `docs/.governance-log.jsonl` 目前的 `kind` 值只有 `warned`/`approved`/`passed`/`skipped` 四種,**沒有 `blocked`**(`grep -o '"kind": *"[^"]*"' … | sort -u` 驗證)。這與文件自己的基線表(第 33 行:`check-r`/`check-j`/`check-k`/`check-e2`/`check-e3` 觸發次數皆為 0)是一致的邏輯結果——這五個 gate 才會寫 `kind:"blocked"`,而它們從沒觸發過,所以 `blocked` 現實中從未出現在帳裡。文件在「讀到的欄位」小節聲稱「本帳實見」`blocked`,與自己第 33 行的基線數字矛盾。不影響演算法行為(收斂指標規則是 `hard=false 且 kind=warned` 才算,其餘一律 n/a,`blocked` 本來就會落在 n/a 分支),純屬文件內部事實陳述前後不一致。

### m2 — 測試 #4 用來驗證「分母為 0」分支的四個來源(code-loop/canary/ci/bypass),實際上全部會被「kind≠warned」規則提前短路,測不到分母為 0 這條路徑本身

引句：「分母 0 → 全欄 n/a 不入桶、不除以零」

實測這四源的 `kind` 值域:`code-loop` 只會是 `passed`/`skipped`(`scripts/lumos:14087-14088`);`bypass`(L2)硬寫字面值 `"kind": "bypassed"`(2912 行);`ci` 的 kind 是 GitHub Actions 的 `conclusion` 值(success/failure/…,2945 行);`canary` 的 kind 依代碼邏輯是 `first`/`second` 一類的審計輪次標記(2932-2938 行)。這四者沒有一個會出現 `kind="warned"`,所以在收斂指標規則裡,它們一律先被「只對 `hard=false 且 kind=warned` 算」(第 84 行)擋下,印 `n/a` 是走這條分支,不是走「分母(相異節點數)=0」那條分支——即便把這四源全部改成 `nodes:[...]` 非空,結果照樣是 `n/a`,因為根本進不到分母計算那一步。测试拿它們当「分母=0」的釘子,驗到的其實是另一條規則,對「分母=0 且不除以零」這條規則本身沒有實質覆蓋(唯一真的會走到「kind=warned 且 nodes 為空」這條路的目前是 `anchor-approve` 的個別列——它 kind=`approved` 也一樣被 kind 規則擋,所以現實中帳本內可能完全沒有任何列會真正跑到「分母=0 且 kind=warned」這個分支;若真是如此,這條規則在目前資料下是死碼,测试策略應该改用構造出的假資料而非四個真實來源舉例)。

### m3 — 「窗口內最後一天」在窗口內零列時無定義

引句：「指窗口內實際出現的最大日期,不是今天。」

若 `--since` 縮到一個範圍內完全沒有任何來源有列(例如 `--since 0` 或未來某個空窗),「窗口內實際出現的最大日期」是空集合的最大值,無定義。此時「輸出首行印實際窗口」(第 101 行)該印什麼——`--since` 請求的原始邊界,還是印「無資料」——文件未答。屬邊角輸入,發生機率低(預設 90 天几乎必有資料),但確實是「輸入落在文件給不出答案的區間」之一,符合本次審查鎖定的洞。

---

## 計數

blocker: 1 / major: 3 / minor: 3
