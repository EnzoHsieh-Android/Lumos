severity: major

## 逐節

### 做法 A:`loop sec-delta` 的參數與輸出

severity: major
blocking: 是 — 實作者得自己猜「空清單」的意思,而且猜錯會讓 S2 的測試和處置閘互相矛盾
引句:「`loop sec-delta` 清單是空的那一份凍結 patch,處置閘的資安席那一步應判涵蓋」
問題:處置閘在凍結 patch 讀不到、或抓不到任何檔名(`not jfiles`)時判 fail,不是涵蓋。`sec-delta` 對「--spec 不是 patch(例如誤傳 .md)」「patch 為空」「patch 是 UTF-8 以外的亂碼」這幾種情況,輸出也是「0 支」。材料沒有定義這幾種輸出,也沒說要印什麼、回什麼退出碼。
具體失敗情境:編排者把 `--spec` 誤傳成計劃 .md,或傳了空 patch。`sec-delta` 印「0 支,清單空」,編排者照 A.3 派一席「確認修補差異沒有新攻擊面」的輕量資安席。處置閘隨後因為 `jfiles` 為空判 fail。S2 的「清單空 ↔ 判涵蓋」在這個輸入上不成立,實作者也寫不出符合它的測試。
佐證:``file: `scripts/lumos:26077` `` 與 ``file: `scripts/lumos:26039` ``(`junread or not jfiles` 這個分支)

severity: major
blocking: 是 — 參數、前置條件、輸出形狀都沒定,三個你點名的情境全都得猜
引句:「印出這份凍結 patch 裡「資安席在這個迴圈裡還沒看過現在這一版」的檔」
問題:有四處沒寫,實作者都得自己決定。
- 沒說 `--repo`/root 怎麼取。帳上的 `snapshot_path` 是相對 repo 根的路徑,`_prov_path` 是 `cmd_loop_status` 裡的內部閉包,`sec-delta` 沒有它就讀不到資安席帳上的凍結 patch。`--spec` 本身若是相對路徑,又該相對哪裡,材料沒說。
- 沒說怎麼找出「資安席的帳」。要靠 `_gated_seats_for(rounds, loop_id)` 取席位,再用 `_auditor_matches_slot` 過濾。材料只說「同一支函式抽出來共用」,沒提這兩個前置。
- 迴圈裡還沒有資安席帳(第 1 輪、或第一次派資安席)時,`_disposal_security_step` 走的是 `if not rows` 的 fail 分支,沒有「看過的檔」可比。`sec-delta` 沒定義這時輸出什麼。合理的答案是列出全部檔並註明「資安席尚無帳」,但材料沒寫。
- 迴圈不是代碼審、或定錨分級沒有必派席、或在生效日前,`_gated_seats_for` 回 skip。`sec-delta` 該印什麼、退出碼多少,材料沒寫。
具體失敗情境:對 design 迴圈跑 `sec-delta`,不同實作者會寫出「照樣算出一份清單」「報錯」「靜默 0 支」三種行為。第三種又會被編排者當成「清單空」,誤以為不用看。
佐證:``file: `scripts/lumos:25965` ``(`_gated_seats_for` 的 skip/fail/apply 三態)、``file: `scripts/lumos:26256` ``(`_prov_path` 是閉包)

severity: major
blocking: 是 — 不共用「帳列留痕驗證」這段,清單和處置閘會分叉,S2 的「同一支比對函式」就不成立
引句:「比對規則就是處置閘資安席那一步現在用的(同一支函式抽出來共用)」
問題:`_disposal_security_step` 的「seen」不是直接從所有資安席帳列取。它先用 `_prov_check` 驗報告與凍結 patch 的 sha,通過的 `good` 列才算看過,留痕壞掉的列整個排除。材料沒說抽出來的共用函式要包含這段驗證,也沒說簽名。實作者最自然的寫法是只抽「`jchg` 對 `seen` 算 unseen/changed」那 3 行,而這 3 行本身只有 `sorted(...)`。這樣 `sec-delta` 會把留痕已被改過或讀不到的資安席帳也算成「看過」。
具體失敗情境:r1 的資安席凍結 patch 檔事後被改。處置閘判資安席「留痕對不上」fail。`sec-delta` 卻照舊印出「只有 a.py 變過」,編排者只派集中看 a.py 的資安席,最後仍被處置閘擋下。
建議的抽法:`(rounds, slot, jchg 來源, prov_path) → (seen, unseen, changed, bad_rows)`,處置閘與 `sec-delta` 都呼叫它。
佐證:``file: `scripts/lumos:26060` ``(`_prov_check` 分流 good/bad)、``file: `scripts/lumos:26082` ``(seen 只收 good)

severity: minor
blocking: 否 — 能實作,但測試可能綠得不實在
引句:「外加支數。比對規則就是處置閘資安席那一步現在用的」
問題:判定輪的凍結 patch 來源不同。處置閘取自判定輪帳列的 `snapshot_path`,`sec-delta` 取自 `--spec`。S2 要求兩邊結論一致,卻沒說測試要讓 `--spec` 指向和判定輪帳列同一份檔。`_sec_loop` 會把 `spec` 與 `snap` 複製成兩個路徑相同內容的檔,碰巧一致。
具體失敗情境:實作者讓 `sec-delta` 讀 `--spec`,測試裡 `--spec` 與帳上 snapshot 內容不同(例如改過再傳),S2 的「清單空 ↔ 判涵蓋」就不成立,而材料沒說這算誰錯。
建議:在做法裡寫明「`sec-delta` 的 `--spec` 必須就是之後要記進判定輪帳的那份凍結 patch」,並讓 S2 的測試明寫這個前提。

### 做法 B:`--residual` 的格式與驗證

severity: major
blocking: 是 — 解析規則沒定,含空白的節點會被切壞;doctor 的驗證會誤報,或默默放行
引句:「寫成 `[audit:模型/日期 殘留:<節點>#<決策 id>]`」
問題:戳記是「模型/日期」加一個空白再接「殘留:…」,而節點路徑可以含空白(圖譜裡中文筆記名含空格是常見的)。材料只示範了無空白的 `Projects/a_計劃#d12`,沒說 doctor 怎麼解析。節點是否可帶 `.md`、是否以 `Projects/` 開頭、決策 id 的格式(`d<數字>`?`#` 之後只要不為空?),全都沒定。同時 `AUDIT_REF_RE` 是 `\[audit:\s*([^\]]+)\]`,節點名一旦含 `]` 就截斷。
具體失敗情境:
- `--residual "Projects/a b_計劃#d12"` 寫進戳記後,doctor 用空白切就切成 `Projects/a` 與 `b_計劃#d12`,節點找不到,報錯。
- `--residual Projects/a_計劃.md#d12` 帶 `.md`。`env.find` 認不認、doctor 認不認、寫進戳記時要不要正規化,材料都沒定。
- `--residual Projects/a_計劃#d12x`、`#12`、`#` 或空字串,有的實作者放行,有的擋,沒有驗收條款把它們釘住。
建議:`guard audit` 寫入時就驗格式 `^(?P<node>.+)#(?P<id>d\d+)$`,以最後一個 `#` 切;拒絕含 `]`/換行的節點、拒絕 `.md` 結尾;並用 `env.find` 正規化。

severity: major
blocking: 是 — 材料沒說在哪支函式驗,也沒說會不會擋寫入,實作者會各自挑一個
引句:「doctor 檢查戳記裡的節點存在、那筆決策存在、沒有被標成 `valid: false`」
問題:現行檢查分兩處:`lint` 的單節點檢查(`invariant_audit_refs(inv)` 只判斷有沒有戳記)和 doctor 的 Check T(只判斷有沒有 `unaudited`)。「節點存在」「那筆決策存在」要跨節點查 `decisions:`,單節點 lint 做不到,所以只能放 doctor。材料沒說放哪一個 Check、報錯時是 rc1 還是只提醒、是否進推送閘。
更要緊的是,`guard audit --residual` 本身在寫入當下不驗,指到不存在的節點或決策也寫得進去,要到 doctor 才被發現。
具體失敗情境:編排者打錯決策 id,`guard audit` 回 `✓ 留痕`;S4 的舊讀者判成已審,pre-push 放行;錯誤要到下次 doctor 才出現,那時殘留決策指向空。
建議:`guard audit` 寫入前就驗(`env.find` 節點、`parse_decisions` 找 id、`valid` 判斷、`content` 非空),與 doctor 共用同一支驗證函式。
佐證:``file: `scripts/lumos:19183` ``(`parse_decisions`)、``file: `scripts/lumos:6722` ``(lint 只看有沒有 audit)

severity: major
blocking: 是 — 重審時殘留會被默默抹掉,還沒有任何條款在防
引句:「沒有殘留照舊 `[audit:模型/日期]`。」
問題:`_cmd_guard_audit_locked` 重審時用 `AUDIT_REF_RE.search(line)` 取代整串舊戳記。新版 `guard audit` 重審同一條合約卻沒帶 `--residual` 時,舊的 `殘留:…` 會被靜默覆蓋。材料只在「回退」節談舊版工具會抹掉,沒談新版自己也會抹。另一個盲點是殘留決策本身被推翻(`valid:false`)時,戳記不會跟著失效,只能靠 doctor 在之後報。
具體失敗情境:第二輪審計時編排者重跑 `guard audit`,忘了再帶 `--residual`。戳記回到「乾淨過」,代碼審席看到的是沒有殘留的合約,卻實際有三型刻意繞過的壞法。
建議:重審時若舊戳記帶殘留而新指令沒帶,要報錯並要求明寫 `--residual` 或 `--drop-residual`。

severity: minor
blocking: 否 — 一般用法不會碰到
引句:「決策 id 只在節點內唯一,所以要帶節點」
問題:材料沒定義 `--residual` 能不能重複給(例如 d12 加另一個節點的 d3)。一條合約的殘留可能分記在多個節點,三個系統節點各記一筆也很自然。
建議:要嘛明寫「只收一筆,多型殘留寫在同一筆決策內」,要嘛規定多筆的分隔格式。

### 驗收條款能不能寫成先紅的測試

severity: minor
blocking: 否 — 工作量問題,不影響能不能做
引句:「舊版讀者(`[audit:]` 的解析與「有沒有審過」的判斷)讀到帶殘留的戳記時,應照舊判成已審。」
問題:S4 在實作前就是綠的。現行 `AUDIT_REF_RE` 吃得下任意字串,手寫一條帶殘留戳記的 KEY 行,現在 lint 就判已審。這條測試不會先紅,沒有鑑別力。要讓它有意義,必須用新版 `guard audit --residual` 寫出戳記,再讀回判斷;這樣紅的原因是指令不存在。建議在 S4 寫明「用 `guard audit --residual` 產出的戳記」,並加翻紅釘:把 `--residual` 的寫入拿掉,S4 要翻紅。

severity: minor
blocking: 否
引句:「[manual: 打開那一段,確認四件事都在,而且沒有要求派工時逐字貼]」
問題:S5 和 S6 是 `[manual:]`,不是機械可驗,與你們「承認風險要附回頭看的條件」的鐵則不一致。S5 的四件事是固定關鍵詞,可以寫成對 `reference.md` 的內容斷言測試(像現有的 `t_templates_security_seat_section`、`t_skill_code_loop_mentions_security_seat`),先紅後綠。S6 同理。目前這兩條純靠人眼,下一輪改 templates 時沒人守。
佐證:``file: `scripts/test_lumos.py:50496` ``、``file: `scripts/test_lumos.py:50513` ``(同類內容斷言測試已有先例)

severity: minor
blocking: 否
引句:「[test: t_guard_audit_residual_stamp]」
問題:S3 把四件事塞進一條測試:寫入格式、節點或決策不存在報錯、`valid: false` 報錯、缺 `valid` 不報錯。條款句式是「應…」的單一可驗行為,一條測試綁四種結果,先紅的順序無法分開。建議拆成 S3a 寫入、S3b 報錯三型、S3c 缺 `valid` 不報錯,或至少在測試名後附子案例。

### 其餘節

做法 A.2、A.3、B 的收斂規則(第 4、5 點)、實務隱患、回退:已讀,無 finding(分類語意與三輪紀律的取捨已有 d12 與 r1 前掃涵蓋,我不推翻)。

最高等級 major,共 5 條 blocking(做法 A 三條、做法 B 三條中的格式解析、doctor 驗證位置、重審覆蓋殘留)。

註:blocking 實際是 6 條——A 三條加 B 三條。

最終計數:最高等級 major,blocking 共 6 條。
