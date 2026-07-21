---
type: project
status: doing
created: 2026-07-21
updated: 2026-07-21
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/全盤外審2026-07_調研]]"
  - "[[Projects/design-loop輕量檔_計劃]]"
  - "[[Projects/lumos-show讀取入口_計劃]]"
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/design-loop]]"
summary: |-
  FLAG:DECISION
  KEY:問題=loop 編排的機械脊椎缺四塊(外審 2026-07-21 順位3 一包,使用者裁「一包到底」):①agent 自己當狀態機(輪數/canary 型別/round-id 全靠散文紀律,lumos-show loop 實戰中 round 編號就錯過一次)②light 收斂無機械謂詞(M0 只能人裁攤牌)③收斂帳無 spec 版本綁定(舊乾淨紀錄可掛新內容,[[Systems/convergence-evidence-gate]] 自認 v2 債)④帳本無成本欄(d5 教義無數字可依)
  KEY:#1 loop next——`lumos loop next <id> [--json] [--tier standard|high|light]` 唯讀讀 canary-log,吐唯一下一動作。gate 委派(r2 C1;r3 修正):完整旗標組委派既有謂詞,--spec 沿現行**可選**語意(G1 skip 仍可 PASS :2684,原 rc2 斷言與現碼相反),converged **附 gate_basis 判定基礎欄**(誠實可稽);**--tier↔gate 模式明定映射**(light⇒--light 謂詞/standard|high⇒panel),衝突組合 rc2(r3);**無 --tier=帳面格式推導**(legacy→width1/cap6,panel→3/3),零記錄 rc2 不猜(r3,原預設 standard 與 cap 判定自相矛盾)。phase **v1 五值**:判定=escalate→**gate-pending(資訊不足,r6 終判:先於 cap——連「未收斂」都判不了時 cap-reached 是假斷言)**→full-basis PASS=converged→cap-reached→plant-canary,互斥窮盡;**rc 契約(r6):converged=0/其餘 phase=1/錯誤=2**。canary 型別(legacy=[(N-1)mod4]/panel=per-slot)+cap 對照(light2/standard3/high3/legacy6)+**--min-seats 數相異 auditor 欄值**(r6:數筆數可被同席重複 append 灌滿;light1/standard3/high5/legacy1)+**tier 定錨**(r6:record 選配 tier 欄首帶定錨,無 --tier 讀帳面,衝突 rc2——否則省略 --tier 的 high loop 被推成 standard 三席收斂)+record 模板。**lumos 只出指針不 spawn agent**;讀側守衛同 status;borrow=git status 式 next-action
  KEY:#2 light 謂詞——`loop status <id> --light --gate`:**單席 caught ∧ 存活 max≤minor ∧ 欄位互證(clean⇒0/minor⇒≥1,復用 :2710;r2 C5) ∧ spec hash 相符(light 強制 fail-closed;r2 C3/C5) → K=1 收斂 rc0**。不含 capture 殘餘(實證 singleton minor 無資訊量)。**ratchet(r2 C5 只吃 caught;r3 分因)**:任一 caught 筆 severity≥major → 永久 FAIL 指路升 standard(-std 後綴承接慣例見分工節);**FAIL 輸出分因 retryable(missed)/ratchet(永久)**——供 next phase=escalate 判讀,否則 next 對 ratchet 態誤吐 plant-canary 與「停、升級」打架(r3);--light 與 --panel 互斥 rc2。pre-flight 排乾維持散文紀律不進謂詞(無機械 oracle,誠實不裝)
  KEY:#3 spec hash——**雙 hash 鏈(r4 Codex 終駁轉正,撤單 hash 範圍刀:單 post-fold hash 證不了 reviewed input,折入引壞版本沒人讀過照樣過閘)**:record --spec 寫 reviewed_sha256(派工當下快照,--reviewed 傳入)+result_sha256(record 當下=post-fold);gate 驗①當前檔=窗 result ②鏈續性 reviewed[n+1]==result[n](折入版本由下輪審計覆蓋;末輪 fold 殘餘=d4 合法逃逸誠實記載)。時序=「fold→fold-check→grep→record」連續收尾(r2 C4+r3 中斷窗第二帳恢復);OSError 兜底 rc2(r1);**收斂窗驗證+窗級 all-or-nothing(r3 輪級→r4 窗級)**:legacy=最後 need 筆全體/panel·light=判定輪,「帶」=雙欄俱全,窗內半帶=FAIL;**鏈模型四件(r6 補④):窗末 result=當前檔/鏈續性/同輪雙欄皆一致(五席四B一C案例堵死)/窗首對稱逃逸**;**帶 --spec 問 gate=聲明要驗,窗內無 hash=FAIL(advisory 僅存不帶 --spec 舊用法)**,light 恆強制;--reviewed 與 --spec 同現否則 rc2(r5)。byte-level 行尾敏感(fail-closed 接受);hash 正確性繫散文步序(隱患誠實記);防誤不防惡
  KEY:#4 成本欄——`canary record [--tokens N] [--wallclock-min N]` 選配數值欄(非負整數,非數值/負值 rc2;不給不寫鍵,同 --findings 慣例);`loop status` 有欄時尾附成本行(逐輪+總計)。跨 loop 統計/升級率報表**不做**(v1 範圍刀,語料累積後另案;北極星已記[[Projects/loop數據收集_計劃]])
  KEY:與[[Projects/design-loop輕量檔_計劃]] M1 分工——本包交付 light 的 loop-status 面(tier 認得+K=1 謂詞+ratchet 機械面);輕量檔 M1 剩餘=進場硬否決機械化(pitfalls 剝自核段,pitfalls/assess 面)留該計劃,兩包互引不重疊
  KEY:落地同步義務(七項,由折入衍生,枚舉寫死)——skills/lumos-design-loop/SKILL.md(record 時序 C4/手算 N 改指 next/light 節人裁改機械 gate)、skills/lumos-design-loop/templates.md(light 附註+模板預設帶 --spec;空帳模板模式由 tier 推導:standard/high→panel 帶 --round、light→legacy)、convergence-evidence-gate KEY「留 v2」清償、loop-convergence-recording 鍵計數、design-loop 手算 N 敘述、輕量檔計劃 M1 標記、Verification 節點
  KEY:★風險面★self-governance=high——四件全動「判定 spec 能否進實作」的閘;進實作前本 spec 必過完整 design-loop(high tier:panel W=5+跨家族否決席+--need 3 精神),同 M2「舊 loop 審新 loop」前例;實作後 pitfalls 必判 tier=high→full code-loop
  TEST:規劃見 body 測試策略——next 三模式指針/light 謂詞矩陣(caught×severity×hash)/ratchet 永久 FAIL/hash 綁定與相容/成本欄驗證與顯示/既有 legacy+panel gate 全迴歸不變
  DEP:[[Systems/loop-convergence-recording]](record 欄位面)｜[[Systems/convergence-evidence-gate]](gate 合取面)｜[[Systems/design-loop]](編排分工)
  PRIOR-ART:①最小解=#2-#4 為既有 record/status 兩指令的欄位旗標擴充;#1 為 loop 子指令組**新增第三個 subparser**(status/capture-counts 之外)——新增一條唯讀查詢介面,**非零新指令**(r1 折入:原「全部零新命令」宣稱與 #1 自相矛盾,自我治理判準不得帶頭失守);仍零新治理層/零新檔 ②世界解=[[Projects/全盤外審2026-07_調研]]本體已裁(#1 Codex 摩擦診斷+git status next-action 普適模式/#3 content-address 綁定=git 血統/#4 OpenAI third-party evals+Anthropic demystifying-evals 把 budget 欄列為 eval 判讀必要上下文) ③裁定=borrow-design 全部(stdlib sha256/argparse 原生)
---
# loop機械脊椎M1包_計劃

> **狀態**：spec 完成，待過完整 design-loop（self-governance=high）。緣起：2026-07-21 全盤外審順位3，使用者裁「一包到底」。四件共用同一批面（`canary record` schema＋`loop status` gate），一份 spec 一次審。

## 問題（全部實戰驗過）

1. **agent 自己當狀態機**：lumos-show loop 四輪全程手工編排——輪數、canary 型別輪替、round-id、severity 記帳全靠散文紀律；實戰中 round 編號（r3/r4）就混過一次。這是日常摩擦最大項（外審 D 類）。
2. **light 收斂無機械謂詞**：M0 首戰收斂只能攤牌人裁——panel gate 要 caught≥2 單席湊不到、legacy G2 被 framing 壓不到底。
3. **spec 版本不綁定**：「審過乾淨」紀錄沒綁「審的是哪一版」——舊乾淨紀錄理論上可掛到改過的新 spec 冒充審訖（gate 節點自認 v2 債）。
4. **成本無帳**：d5「成本平衡」教義沒有數字可依；light 省多少、哪類 spec 審最貴，答不出來。

## 規格

### #1 `lumos loop next <id> [--json] [--tier standard|high|light]`

- **唯讀**：讀該 loop 的 canary-log（同 `loop status` 的讀側守衛：round 混用/損壞 clusters/非連續 round-id → 同款 rc2），不寫任何檔、不 spawn agent——**lumos 只出指針，編排仍是 Claude**（維持 [[Systems/design-loop]]「Claude 編排,lumos 出原語」分工）。
- **gate 參數委派（r2 C1；r3 basis 欄；r4 Codex 再駁——basis 標註擋不住機讀端只看 phase 放行）**：next 接受完整 gate 旗標組委派既有謂詞、不改 status 行為（`--spec` 對 status 可選是現行語意 :2684）。**r4 收口：next 的 `converged` 只在 full-basis 時輸出**（G1 run ∧ hash verified，如適用）——缺 `--spec` 等資訊不足時 phase 輸出第五值 **`gate-pending`**（「帳面或可收斂，但 next 資訊不足以背書；請自行跑 `loop status --gate` 附完整參數」），**絕不輸出 converged**。code-loop 無-spec 用法不受影響（它直接用 status，不經 next）。
- **`--tier` 與 gate 模式調和（r3 折入——兩套旗標無調和會產出錯陣容/誤報未收斂）**：明定映射——`--tier light` ⇒ gate 委派走 `--light` 謂詞；`--tier standard|high` ⇒ panel 謂詞。**衝突組合一律 rc2**（`--tier light --panel`／`--tier standard --light` 等），不留「誰贏」猜題。
- **無 `--tier` 的身分推導（r3 折入；r7 Codex 終確認統一——原兩處「預設 standard」殘句與 tier 定錨規則分叉，high 可被合法降 standard）**：**定錨優先**——①帳面有 tier 定錨（首個帶 tier 欄的記錄）→ 一律用定錨值（high 定錨即 width=5/min-seats=5，永不 fallback）；②無定錨（本功能上線前的舊帳）→ 帳面格式推導（legacy 格式→width=1/cap=6；panel 格式→**僅此 fallback** standard width=3/cap=3）；③零記錄 → rc2 要求明示 `--tier`（不猜）。
- **空帳模板模式明定（C1 附帶）**：`--tier standard|high` → panel 格式（帶 `--round`）；`--tier light` → legacy 單席格式（不帶 round）。
- **輸出（人讀預設；`--json` 機讀）**：
  - `phase`（**v1 契約=五值**，r1 砍死值；r3 補 escalate；r4 補 gate-pending）：`plant-canary` / `converged`（僅 full-basis） / `gate-pending`（資訊不足不背書） / `cap-reached` / `escalate`（light ratchet 已觸發——指路「停止本 loop，開新 panel loop id 承接」）。
  - **判定優先序（r1 cap；r3 escalate；r5 gate-pending；r6 Codex 終判折入——gate-pending 必須先於 cap：資訊不足時連「未收斂」都判不了，吐 cap-reached 是假斷言）**：⓪ light ratchet 已觸發 → `escalate`；① gate 判定資訊不足（缺 `--spec` 等）→ `gate-pending`（**先於 cap**——「補齊參數可能即 PASS」）；② full-basis PASS → `converged`；③ `輪數 ≥ cap`（資訊充分且未 PASS）→ `cap-reached`；④ 其餘 → `plant-canary`。五分支互斥窮盡。
  - **rc 契約（r6 折入——原全未定義，機讀端會分岔）**：`converged`=rc0；其餘四 phase=rc1；參數/IO/帳損壞=rc2（對齊 status 三值慣例 :2610）。
  - light gate 的 FAIL 分因 retryable（missed）/ratchet（永久）。
  - `round`：下一輪 N（= 現有輪數＋1，legacy 記錄數／panel round 分組數）。
  - `canary_type`：legacy＝`清單[(N-1) mod 4]`；panel＝per-slot 輪替表（slot i → `清單[(i+N-1) mod 4]`）。
  - `width`：tier→席數（light=1／standard=3／high=5；`--tier` 不給→**依身分推導（定錨優先，見上；r7 統一——舊「預設 standard」句撤）**；**tier 是編排者宣告後定錨，lumos 只做映射與定錨讀取**）。
  - `record_cmd`：該輪記帳指令模板字串（含 loop id／round-id／建議旗標——模板是提示非強制）。
- **cap（r1 折入：tier→cap 直給對照表）**：`light=2`／`standard=3`／`high=3`／legacy 格式=6。硬編碼進 next，與 skill 漂移時以 code 為準並回寫 skill。
- **席數下限（r4 新 major；r5 legacy 值；r6 Codex 終判雙補——①數記錄筆數可被同席重複 append 灌滿 ②tier 不持久化，下次省略 --tier 的 high loop 被推成 standard 三席即收斂）**：gate 選配 `--min-seats N`（不帶=現行為不變）；判定輪**相異 `auditor` 欄值數** < N → FAIL「席數不足」（數相異席非筆數——schema 既有欄零新欄，重複席不計）。**tier 持久化**：record 加選配 `--tier` 欄，該 loop 首個帶 tier 的記錄**定錨 loop tier**（同定錨前例）；next/gate 無 `--tier` 時讀帳面定錨值（無欄舊帳→format 推導）；明示 `--tier` 與帳面定錨衝突 → rc2。next 自動傳 min-seats：light=1／standard=3／high=5／legacy=1。

### #2 light K=1 謂詞：`loop status <id> --light --gate`

- **收斂合取（K=1；r2 Codex 折入 C5 補全）**：末輪（該 loop 最新一筆）`caught` ∧ 存活 `severity ∈ {clean, minor}` ∧ **欄位互證（復用 :2710 既有檢查：clean⇒findings=0、minor⇒findings≥1，矛盾即擋）** ∧ **hash 相符（light 為新賽道無存量包袱——hash 雙欄（`reviewed_sha256`/`result_sha256`，r5 欄名同步）缺任一=FAIL 非 advisory，fail-closed 強制啟用；K=1 單輪窗鏈檢查空轉、僅①當前檔==result 生效——reviewed 為 mandated-but-unverified，誠實觀察記載）** → **GATE PASS rc0**。
- **不含 capture-recapture 殘餘**——2026-07-21 實證：singleton minor findings 使殘餘估計恆高（6.0-15.0），對「小 spec 一輪乾淨」場景零資訊量（見 [[Projects/design-loop輕量檔_計劃]] M1 前置發現③）。
- **ratchet 機械面（只升不降；r2 Codex 折入 C5：只吃 caught）**：該 loop 任一筆 **`caught`** 記錄 severity ≥ major → `--light` gate **永久 FAIL**（rc1），訊息指路「light 已 ratchet，升 standard：開新 panel loop id 承接（同 lumos-show 前例；承接時的 id 命名與紀錄歸屬見〈與輕量檔 M1 的分工〉節）」。**missed 筆的 severity 不觸發 ratchet**——missed 輪判決不採信是既有教義（SKILL:43），不可信裁決不得擁有永久否決權；missed 只使該輪不可收斂（light cap=2 內重試，見 cap 表）。不可用後續乾淨輪洗回 light。
- **互斥**：`--light` 與 `--panel` 同給 → rc2。`--light` 對帶 round 的 panel 記錄 → rc2（light=legacy 單席記錄格式，同 lumos-show light r1 實例）。
- **pre-flight 不進謂詞**：排乾與否無機械 oracle（是散文 checklist），謂詞不裝可驗——維持 skill 層紀律，誠實記載此限制。

### #3 spec hash 綁定：`canary record --spec <path>`

- **時序裁定（r2 Codex C4；r3 折入中斷窗防護）**：現行權威流程是**先 record（步驟5）後 fold（步驟7）**——照此 hash 必在每個有折入的 caught 輪後失配。**本包裁定：調整 skill 時序**——caught 輪改為「fold → fold-check → canary token grep=0 → record」**連續收尾序列**（missed 輪無 fold，record 即收尾不變）。**中斷窗（r3）**：時序移位把「派了沒記」窗擴大為「折了沒記」——crash 落在已折未記時，該輪 log 零痕跡、next 會重發同 N、caught+major 的 ratchet 訊號蒸發。防護＝**spec 審計修正紀錄是第二帳**：恢復規則「log 無該輪 record 但 spec 審計紀錄有該輪條目 → 人工補 record 再繼續」，寫進 skill 收尾段；隱患節記載此窗。此為 skill 文字改動，列入同步義務；spec 不假裝這是既有慣例。
- **雙 hash 鏈（r4 Codex 終駁折入——單 post-fold hash 證不了「審過的輸入」：折入引壞的版本沒人讀過照樣過閘。撤 v1「單 hash」範圍刀，Codex r1 原案轉正）**：record 帶 `--spec <path>` 時寫**兩欄**——`reviewed_sha256`（**派工當下**真檔快照：skill 步驟 1 複製工作副本時順手 `sha256sum 真檔` 留存，record 以 `--reviewed <hex>` 傳入）＋ `result_sha256`（record 當下真檔＝post-fold）。gate 驗兩件：①當前檔 == 收斂窗 `result_sha256`（防審後改）②**鏈續性**：第 n+1 輪 `reviewed_sha256` == 第 n 輪 `result_sha256`（保證「折入的版本正是下輪審的版本」——折後內容由下輪審計覆蓋）。**末輪 fold 殘餘**（最後一輪折入的內容無下輪覆蓋）＝d4 定位的合法逃逸（正確性歸下游 code-loop＋測試），誠實記載非掩蓋。
- **讀檔/hash 失敗一律 rc2（r1 折入）**：不存在/是目錄/無權限等統一 `OSError` 兜底——沿 G1 :2687-2691 catch 慣例。
- **寫側同現規則（r5 折入——`--reviewed` 孤給未定義，會生出半欄記錄汙染窗判定）**：`--reviewed` 與 `--spec` **必須同現**，單給任一 → rc2「hash 雙欄必須成對」。
- **讀側（r2「末筆→末輪」→r3「收斂窗」→**r5 折入：讀側全面改寫為鏈模型，兩席互證抓出「line 73 仍留單 hash 全等模型與鏈模型打架——窗內含 fold 時全等恆假=誤擋一切真收斂」**）**：三模式 gate 帶 `--spec` 時以**收斂窗**（legacy＝最後 `need` 筆；panel/light＝判定輪）為範圍，驗**鏈模型四件（r6 Codex 終判補④——同輪只驗 reviewed 一致漏了 result：五席四筆 result=B 一筆=C、當前檔=C 照樣過閘）**：① 窗**末**筆 `result_sha256` == sha256(當前 `--spec` 檔)；② 窗內**鏈續性**：相鄰有效輪 `reviewed[k+1] == result[k]`；③ **同輪 round-level invariant：雙欄皆須輪內一致**——所有席 reviewed 彼此相等**且**所有席 result 彼此相等，任一欄分裂 → FAIL「同輪宣稱多個版本」；④ 窗**首**筆 reviewed 無窗內錨點——與末輪 fold 殘餘對稱的已知逃逸，誠實記載不硬驗。鏈只在收斂窗內連續有效輪間檢；missed/窗外輪不參與相鄰性（r5 明文）。任一驗證不過 → FAIL 附分因訊息。
- **「帶 hash」＝雙欄俱全（r5 折入——舊欄名 spec_sha256 已拆 reviewed/result 兩欄，「帶」的定義必須跟上）**：記錄「帶 hash」＝`reviewed_sha256` 與 `result_sha256` **兩欄俱全**；只有其一＝半帶。**收斂窗 all-or-nothing**（r3 輪級→r4 窗級）：窗內任一筆帶 ⇒ 全體必須帶（雙欄），半帶 → FAIL「收斂窗 hash 半帶——收斂憑證無法互證」。定錨語意窗級；無時序先後。
- **相容（r2 C3；r3 輪級化；r4 Codex 再駁收口——「整條不帶=advisory」就是原逃生門換名）**：**gate 帶 `--spec` = 消費者聲明要 hash 驗證 → 收斂窗內無任何 hash = FAIL**（「帳未綁定——請重審一輪並於 record 帶 --spec」），非 advisory。advisory 僅存於 gate **不帶** `--spec` 的舊用法（存量 loop 不重跑 gate 即不受影響；重跑=要求重新背書，fail-closed 合理）。light 恆強制。逃生門閉合：攻擊場景（無 hash 帳＋改檔＋帶 --spec 問 gate）現為 FAIL。
- ~~v1 單筆 hash~~（r4 撤刀改雙 hash 鏈，見上）；本機制仍**防誤不防惡**（本地 jsonl 可改，誠實天花板同 evidence-gate 既有條）。

### #4 成本選配欄：`canary record [--tokens N] [--wallclock-min N]`

- 寫側：兩欄皆選配、皆須非負整數（非數值/負值 → rc2）；不給不寫（鍵不存在，同 `--findings` 慣例）。
- 讀側：`loop status` 任一筆有成本欄時，輸出尾附成本區（逐輪 tokens/分鐘＋總計）；全無則不印（零噪音）。
- **範圍刀**：跨 loop 統計、升級率報表、成本門檻**全不做**——v1 只記帳與單 loop 顯示；北極星與跨 loop 分析歸 [[Projects/loop數據收集_計劃]]（語料累積後另案）。

## 與輕量檔 M1 的分工

本包交付 light 的 **loop-status 面**（`--light` 謂詞＋ratchet 機械面）；[[Projects/design-loop輕量檔_計劃]] M1 剩餘＝**進場硬否決機械化**（pitfalls 剝「light 資格自核」段再掃，pitfalls/assess 面）留在該計劃。兩包互引、無重疊面。

**ratchet 承接 id 慣例（r3 折入——原 ratchet 訊息指本節卻無此內容，懸空引用修復）**：light ratchet 後開新 panel loop id＝**原 id ＋ `-std` 後綴**（lumos-show 前例：`lumos-show讀取入口` → `lumos-show讀取入口-std`）；舊 light loop 紀錄原地保留不遷移，新 loop record note 首筆註明「承 <原id> ratchet」。

## 落地同步義務（同 commit；由折入內容衍生，比照 lumos-show 前例枚舉寫死）

1. `skills/lumos-design-loop/SKILL.md`：〈每一輪〉record 時序改動（C4）；步驟 1「N 手算」改指 `lumos loop next`；**步驟 1 加「複製工作副本時 `sha256sum 真檔` 留存 reviewed hash」義務（r5 折入——雙 hash 寫側派工義務漏列）**；〈light 檔〉步驟 4 人裁出口改機械謂詞。
2. `skills/lumos-design-loop/templates.md`：§1 light 附註同步；派工/記帳模板預設帶 `--spec` **與 `--reviewed <hex>`（成對，r5）**；派工模板加 dispatch-time hash 計算指引。
3. `Systems/convergence-evidence-gate`：KEY 行「--spec 無綁定向量**留 v2**」——#3 落地即清償，同 commit 拿掉「留 v2」改記落地指針；FLOW 的 gate 合取敘述補 hash 條件式說明（定錨後 FAIL 非 advisory）（r3 觀察折入）。
4. `Systems/loop-convergence-recording`：record 選用鍵計數與清單（+`reviewed_sha256`/`result_sha256`/`tokens`/`wallclock_min`——r5 欄名同步，舊單欄名已撤）。
5. `Systems/design-loop`：〈每一輪〉手算 N 敘述同步 loop next；**FLOW 摘要行的「canary record→折真檔」順序句一併改**（r3 折入——C4 時序落地後該句與新行為相反，漏改＝SSOT 內漂移）。
6. `Projects/design-loop輕量檔_計劃`：M1 的 loop-status 面標記由本包交付。
7. Verification 節點（plan_refs 回指本計劃）。

## 明確不做（範圍刀）

- `loop next` 不寫狀態、不 spawn agent、不判 tier（編排者宣告）；phase 不偵測「派了沒記」（log 看不見派工）。
- ~~不做雙 hash 鏈~~（r4 Codex 終駁後轉正為 v1 必要件——單 hash 語意撐不住「審過的輸入」證明）；不做跨 loop 成本報表；不做 escape ledger（外審 #5，獨立小 spec 另案）；不動 legacy/panel 既有 gate 合取**本體**（新增 hash/min-seats 皆為選配疊加，不帶=行為不變）。

## 測試策略

- **next**：空 loop→plant-canary N=1／有 FAIL 記錄→N+1＋型別輪替正確（legacy mod4、panel per-slot）／gate 可過→converged／達 cap→cap-reached／`--json` 結構完整／混用帳 rc2 同 status／`--tier` 三值→width 映射／不存在 loop id 行為明確。
- **light 謂詞**：矩陣——caught+clean→PASS／caught+minor→PASS／caught+major→FAIL 且此後**永久** FAIL（ratchet，後續乾淨輪不洗回；FAIL 分因 retryable/ratchet）／missed→FAIL 不觸發 ratchet／欄位互證矛盾（clean+findings>0）→FAIL／--light+--panel rc2／--light 對 panel 記錄 rc2／**hash 缺失=FAIL（light 強制 fail-closed，r4 同步——原「advisory 不擋」行違反 light 語意）**。
- **hash（r4 收斂窗/雙鏈；r6 終判補列）**：--spec 記錄雙欄正確／檔不存在/目錄 rc2／收斂窗驗證（legacy need 筆全體）／窗內半帶=FAIL／鏈續性斷鏈 FAIL／**同輪 result 分裂 FAIL（五席四 B 一 C 案例）**／**--reviewed 或 --spec 單給 rc2**／改檔後 FAIL 訊息正確／帶 --spec 窗內無 hash=FAIL／不帶 --spec 舊用法不變／**窗首無錨・missed 不參與鏈・light K=1 空鏈（三個已知逃逸行為明確）**。
- **next/gate 契約（r6 終判補列）**：**gate-pending 先於 cap**（到 cap 且缺 --spec → gate-pending 非 cap-reached）／**五 phase rc 契約**（converged=0/其餘=1/錯誤=2）／`--min-seats` **數相異 auditor**（同席重複 append 不計）／**tier 定錨**（首帶 tier 記錄定錨、無 --tier 讀帳面、衝突 rc2、省略 --tier 的 high loop 不得被推成 standard）。
- **成本欄**：數值寫入／非數值/負值 rc2／不給不寫鍵／status 顯示逐輪+總計／全無不印。
- **迴歸**：既有 legacy gate（K-streak∧G1∧G2）、panel 三條合取、cluster 帳、混用守衛——全部現行測試不紅（不動語意）。

## 審計修正紀錄

**pre-flight（2026-07-21，haiku checklist）**：0 命中（六項全過——今天實戰紀律直接反映在 spec 起點）。

**r1（2026-07-21，high panel W=4 sonnet 異鏡頭＋Codex 否決席；loop id `loop機械脊椎M1包`）**：canary slot1=a 型（近名假節〈分工與邊界〉，probe 重植 1 次後 pass）✗ missed；slot2=b 型（測試單憑空旗標，probe 重植 1 次後 pass）✗ missed；slot3=c 型（憑空分塊常數）✓ **精準抓**（grep 零命中＋反先例 :6382/:6414 整檔讀無分塊）；slot4=d 型（憑空狀態表檔名，probe 直接 pass）✗ missed。**caught 1/4=輪無效**；三 missed 席 findings 依規則全數剔除（其中含貌似高值貨——ratchet 被 missed-severity 毒化、panel 末筆語意——不走後門撿，留醒席與否決席浮回）。護欄觸發（連 2 筆 missed 條件在本 loop 帳成立）→ r2 升 opus。**編排者偏離自省（記入 M1 回饋）**：slot2/slot4 的 canary 植在該席鏡頭責任田之外——missed 率混入 lens-scoping 因素非純放水訊號；panel canary 植入紀律應加「型別異段＋落在該席專攻範圍內」雙條件。
slot3（醒席）7 條折入 v2：
- **F1 phase 判定順序（major）**：cap 檢查改短路優先＋三分支互斥窮盡——原字面 if/elif 順序使 cap-reached 永不可達、next 誘導無限燒（違「到頂停」硬教義）。
- **F2 `--spec` 讀檔失敗面（major）**：只查存在性會對目錄裸 traceback——統一 OSError 兜底 rc2，沿 G1 :2687-2691 慣例。
- **F4 PRIOR-ART 自相矛盾（minor）**：「零新命令」與 #1 新 subparser 打架——自我治理判準不得帶頭失守，改誠實版。
- **F5 hash 行尾敏感（minor）**：CRLF/正規化觸發無資訊量重審——v1 接受並記載。
- **F6 phase 死值（minor）**：record/gate 從 v1 契約拿掉（防消費端死分支）。
- **F7 light cap 缺數（minor）**：補 tier→cap 直給對照（light=2/standard=3/high=3/legacy=6）。
- **F8 loop id typo 不可分辨（minor）**：既有結構限制記入隱患。

**r2-Codex（2026-07-21，否決席 gpt-5.6-sol high，108k tokens，無 canary 約束）**：**VETO，5 major 全折入 v3**——其中 C2/C4/C5 後半＝被剔除 missed 席真貨的跨家族獨立再發現（機制二度自證：剔除規則不吞真信號，真貨從可信通道浮回）：
- **C1 next 輸入不足不得宣告 converged（major）**：gate 合取依賴 --need/--spec/--repo/--panel——next 改為完整 gate 旗標組委派既有謂詞，資訊不足 rc2 絕不輸出 converged；空帳模板模式由 tier 確定性推導（standard/high→panel、light→legacy）。
- **C2 末筆→末輪 hash（major）**：append 補一筆可繞過整輪重審——升級為判定輪內全帶-hash 記錄彼此一致∧=當前檔，輪內漂移即 FAIL。
- **C3 advisory 永久逃生門（major）**：新 loop 可永不啟用——定錨式啟用（帶過即必須帶到底）＋light 強制 fail-closed＋工具鏈模板預設帶 --spec 收窄；殘餘（整條不帶）誠實記載。
- **C4 record/fold 時序顛倒（major）**：現行為先 record 後 fold，原 spec 斷言相反——裁定調整 skill 時序（caught 輪 record 移 fold 後收尾），列同步義務，不假裝既有慣例。
- **C5 light 謂詞漏欄位互證＋ratchet 吃 missed（major）**：補 clean⇒0/minor⇒≥1 互證（復用 :2710）；ratchet 改只吃 caught 筆 severity（missed 判決不採信教義）。

**r2（2026-07-21，opus×4 升級席（護欄），canary in-lens＋植 diff hunk 內；Codex 復核另記）**：canary slot1=b 型（憑空模板旗標）✓ slot2=c 型（憑空門檻常數）✓ slot3=d 型（憑空快取檔——連引用前例實碼零快取都挖出）✓ slot4=a 型（憑空章節）✓——**4/4 caught、0 missed=輪有效**（護欄升級＋in-lens 植入紀律立竿見影，對照 r1 sonnet 1/4）。真 findings 去重 7 major＋3 minor 折入 v4：
- **S1-FC1（major）**：v3「缺 --spec rc2」斷言與現行 status 相反（--spec 可選、G1 skip 仍可 PASS :2684）——改「委派沿現行語意＋converged 附 gate_basis 判定基礎欄」，誠實可稽不改 status。
- **S1-F-CAP（major）**：無 --tier 預設 standard 與 cap 的 legacy 判定自相矛盾——改帳面格式推導（legacy→1/6；panel→3/3）＋零記錄 rc2 不猜。
- **S2-FA（major）**：hash 只驗末輪使 legacy K=2 中間輪逃綁定（K=2 靜默降 K=1）——驗證範圍改「收斂窗」（legacy=最後 need 筆全體）。
- **S2-FB＋S3-FC（major，兩席互證）**：定錨「後續」逐筆時序讓定錨輪內錨前席 grandfathered——改輪級 all-or-nothing（任一帶⇒全帶，半帶 rc2）＋定錨語意輪級化。
- **S2-FC（major）**：--tier 與 gate-mode 旗標無調和（--tier light 不蘊含 --light 閘→對已收斂 light 誤報未收斂）——明定映射＋衝突 rc2。
- **S3-FA（major）**：ratchet 態下 next 吐 plant-canary 與「停、升級」打架（最常見 light-found-major 路徑）——phase 補第四值 `escalate` 最先短路＋light FAIL 分因（retryable/ratchet）。
- **S3-FB（major）**：C4 時序開「折了沒記」中斷窗（重派已折輪＋ratchet 訊號蒸發）——收尾連續序列＋審計紀錄第二帳恢復規則。
- **S4-F1（major）**：同步義務漏 design-loop FLOW 的 record→fold 順序句——第 5 項擴列。
- **S4-F3（minor）**：ratchet 訊息懸空引用——分工節補 `-std` 後綴承接慣例。
- **S3-FE（minor）**：hash 正確性繫散文步序——隱患誠實記載。
- **S4-觀察（minor）**：evidence-gate FLOW 合取敘述補 hash 條件式——同步義務第 3 項擴。

**r2-Codex 復核（2026-07-21，150k tokens，皆附可執行反證）**：C5 解除；**C1-C4 未解除、2 新 major，VETO 維持——全折入 v5**：
- **C1 再駁**：basis 標註擋不住機讀端只看 phase 放行 → converged 僅 full-basis 輸出；資訊不足改吐第五值 `gate-pending`，絕不背書。
- **C2 再駁**：legacy K=2 窗「首筆無 hash 次筆定錨」照穿 → all-or-nothing 升收斂窗級（跨輪窗半帶=FAIL）。
- **C3 再駁**：「整條不帶=advisory」即原逃生門 → gate 帶 --spec=消費者聲明要驗，窗內無 hash=FAIL；advisory 僅存不帶 --spec 舊用法。
- **C4 終駁（本輪最深）**：單 post-fold hash 證不了 reviewed input——折入引壞版本沒人讀過照樣過閘 → **撤單 hash 範圍刀，雙 hash 鏈轉正**（reviewed/result 兩欄＋鏈續性 reviewed[n+1]==result[n]；末輪 fold 殘餘=d4 合法逃逸誠實記載）。
- **新 A**：測試策略行仍鎖舊語意（light advisory 不擋/驗末筆）→ 全單同步 v5 語意。
- **新 B**：panel 謂詞不知 width、high 兩席可收斂 → gate 選配 `--min-seats`（next 依 tier 自動傳），五席承諾機械兌現。

**r3（2026-07-21，cap 末輪，opus×2 delta＋haiku 哨兵＋Codex 終局另記）**：canary slot1=c 型（憑空映射表名）✓ 精準抓（三處落差）；slot2=d 型（憑空核對單檔）✓ 精準抓（NOT FOUND＋ls 證無）。**2/2 caught、0 missed=輪有效**。真 findings 4 major＋2 minor 折入 v6——全是「v5 改標題段漏散落面」的病（正中已知病灶，自家 spec 也逃不掉）：
- **S1-F1＋S2-F1（major，兩席互證）**：讀側 line 73 仍留單 hash 全等模型與鏈模型打架——窗內含 fold 時「全等」恆假=誤擋一切真收斂；舊欄名 spec_sha256 散落 4 處。折入：讀側全面改寫鏈模型三件（末筆 result==當前檔/鏈續性/窗首對稱逃逸）＋欄名全同步。
- **S1-F2（major）**：gate-pending 沒進 body 判定優先序（仍寫四分支窮盡）——照 body 實作漏第五值退回背書。折入：五分支＋②′ 明確落點。
- **S2-F2（major）**：同步義務未跟上雙 hash 寫側（步驟 1 reviewed hash 義務/模板 --reviewed）。折入：item 1/2 擴列。
- **S2-F3（major）**：--reviewed 孤給未定義＋「帶 hash」雙欄完整性未定義。折入：同現規則 rc2＋雙欄俱全定義。
- **S1-F4（minor）**：min-seats 缺 legacy 值→補 legacy=1。**S2-F4（minor）**：鏈相鄰性/窗首邊界明文。
- 哨兵：僅行號慣例雜訊（advisory 無料）。slot1 觀察：light K=1 鏈空轉（reviewed mandated-but-unverified）——誠實記入 light 合取。

**r3-Codex 終判（2026-07-21，124k tokens）**：C2/C3 **解除**（收斂窗＋雙欄俱全＋聲明式 FAIL 收口確認）；C1/C4/新A/新B 未解除、VETO 維持——**四條確定性修法全折入 v7**：
- **C1 殘**：gate-pending 必須**先於** cap（資訊不足時連「未收斂」都判不了，cap-reached 是假斷言）＋ **rc 契約明定**（converged=0/其餘 phase=1/錯誤=2，對齊 status 三值 :2610）。
- **C4 殘**：同輪只驗 reviewed 一致漏了 result——五席四筆 result=B 一筆=C、當前檔=C 照樣過閘 → 鏈模型補④ round-level invariant 雙欄皆輪內一致。
- **新A 殘**：測試單補 gate-pending×cap／rc 契約／單給 rc2／同輪 result 分裂／三個已知逃逸行為／席去重／tier 定錨。
- **新B 殘（雙 major）**：min-seats 數記錄筆數可被同席重複 append 灌滿 → 改數**相異 auditor 欄值**（既有欄零新欄）；tier 不持久化、省略 --tier 的 high loop 被推成 standard 三席收斂 → **record 加選配 tier 欄、首帶定錨、衝突 rc2**。
- **處置**：cap 3 輪已滿（Codex 復核不佔輪，前例一致）；v7 折入後請否決席終確認，帶其判決攤牌人裁。

## 實務隱患

- **self-governance 循環（最重）**：四件全動「判 spec 能否進實作」的閘——gate 邏輯錯＝系統性放行壞 spec 或永擋好 spec。緩解＝本 spec 過完整 design-loop（high：W=5＋跨家族否決席）＋測試逐條對齊謂詞矩陣＋實作後 full code-loop（pitfalls 必判 high）。
- **loop next 的權威錯覺**：next 吐的是**指針非命令**——editor 若把模板當絕對真相（如 tier 給錯→width 錯），會系統性走錯陣容。緩解＝輸出頭印「advisory：tier 由編排者宣告」＋skill 派工模板仍為權威。
- **light ratchet 的 loop-id 邊界**：ratchet 永久 FAIL 綁 loop id——換 id 就洗掉（同 evidence-gate「換 loop_id 洗紀錄」既有天花板）；hash 綁定收窄但不封死此路。誠實記載，v2 spec-hash 綁 loop 可再收。
- **成本欄 GIGO**：tokens/wallclock 是編排者自報——謊報不可偵測；帳的價值在趨勢非單筆精度（同 anchors GIGO 條）。
- **cap 硬編碼雙源**：next 的 cap 與 skill 文字雙處宣告——漂移風險；以 code 為準、skill 回寫。
- **hash 對行尾/編碼敏感（r1 折入）**：byte-level sha256——跨機器 autocrlf/編輯器正規化會使「語意未變」的檔判成「被改動」觸發無資訊量重審。fail-closed 方向（誤擋非誤放）；v1 接受不緩解（單機工作流為主），記載此成本。
- **loop id typo 不可分辨（r1 折入，既有結構限制）**：無 loop 註冊表——打錯 id 與開新 loop 在 next 眼裡同為零記錄，無法提醒（零記錄現改 rc2 要 --tier，略收窄但不解 typo 本身）。`loop status` 現況同病，非本包引入。
- **hash 正確性繫於散文步序（r3 折入）**：C4 新時序（fold→record）無機械強制——編排者沿舊肌肉記憶 pre-fold record，hash 即綁錯版、日後對「沒被改過」的 spec 誤報「被改動」。與「無機械 oracle 不進謂詞」同級誠實記載：這條 gate 合約的正確性建在 skill 步序紀律上，fail 方向=誤擋非誤放。
