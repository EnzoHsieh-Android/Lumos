severity: major

# 架構對齊審查:存量漂移防線_計劃 r2

範圍:只判「跟本專案既有做法一不一致」,不找 bug、不評風格。對照物:`scripts/lumos` 裡筆記形狀擋(note-shape)、筆記內容審(note-audit)、每支檔有家(node-home)、guard plan/settle/abandon、`lumos set`、lint-waive、`[since:]`/`[until:]`/`[retire:]`/`[confirmed:]`/`[status:]`、`valid_under`/`revalidate_when`(COND_KEYS)、drift-history。程式碼路徑一律指凍結快照對照的 repo(`/private/.../scratchpad/clone-ns`)。

## 問1:分層與依賴方向

新指令族 `lumos drift`(check/scan/ack/exam)在設計上跟既有兩層筆記閘(note-shape、note-audit)同級,都是「讀被檢查版本的樹、算差異、寫治理帳」的推送閘家族,沒有發現它跨層直呼底層原語或繞過共用函式自己再刻一套。逐項核對 spec 的〈PRIOR-ART〉借用清單:

1. 推送範圍起點:`_lens_push_base(repo_root, a, tip)` 簽章與行為(40 個 0/本機找不到/走 merge-base)跟 spec 〈做法〉第 0 節描述一致 — file: `scripts/lumos:29220`
2. 上線點截斷:`_nodehome_clamp_base(repo_root, base, tip, mark=None, hook=...)` 用 `-S<mark>` 找掛鉤裡第一次出現標記的提交,跟 spec「截到自己的上線點(推送前掛鉤裡出現標記 `drift check` 的第一個提交)」的做法同一支 — file: `scripts/lumos:22967`、`scripts/lumos:22956`(`_nodehome_golive`)
3. 讀某提交的樹:`_nodehome_reader(repo_root, where)` 簽章與「跟磁碟一樣的直接讀磁碟,不一樣的用 git show」行為與 spec 敘述一致 — file: `scripts/lumos:22551`
4. 測試檔判定:`_nodehome_is_test(path, layout=({}, {}))` 存在且是路徑規則(不讀工作目錄索引),跟 spec「④測試檔判定借 `_nodehome_is_test`」一致 — file: `scripts/lumos:22453`
5. 狀態欄位同步:`edit_fm_sync_status_tag(fm_lines, status)` 就地改 `tags` 裡 `status/*` 項,`cmd_set` 唯一呼叫點在 `_cmd_set_locked` 裡 — file: `scripts/lumos:13956`、`scripts/lumos:14329`
6. 寫入與鎖:`atomic_write_verify(path, new_lines, key, expected_check)`(寫 tmp→自驗→原子換名)與 `_vault_write_lock(vault)`(可重入、鎖檔放 `~/.cache/lumos/vault-lock/`)都存在,`cmd_set` 本身就是 `with _vault_write_lock(env.vault): return _cmd_set_locked(...)` 這個形狀 — file: `scripts/lumos:14181`、`scripts/lumos:14251`、`scripts/lumos:14300`
7. 內容編號:`_notelines_content_id(path, region, heading, line, done=False)` 簽章跟 spec「借 `_notelines_content_id`:路徑、區塊、小標題、行文字」一致 — file: `scripts/lumos:23822`
8. git 逾時:`_lens_git` 硬編 `timeout=20`,跟 spec「單次沿用 `_lens_git` 的 20 秒逾時」一致 — file: `scripts/lumos:29249`(`timeout=20` 在同函式內)

一處看起來像「不經 `cmd_set`、直接呼叫 `atomic_write_verify`」的地方查過是合理的,不是繞過:`guard plan` 寫的三種預告句(`TEST:`/`WHY:`/`為什麼還不做:`)實際落在**守衛節點本身的 body**(`_guard_plan_write_node`,file: `scripts/lumos:11552`),而 `cmd_set` 只能改 frontmatter 純量欄位(`edit_fm_scalar`),沒有能力改 body 散文行。現在 `cmd_guard_settle` 對 body 完全不碰,只用 `cmd_set(env, rel, "status", "pass")` 換 `status` 一個欄位(file: `scripts/lumos:11834`)——這正是 rtb 根因回饋要修的「轉正後預告句留在原地變過期存量」那個洞。spec 把「status + 標籤同步 + 三句型改寫」併成一次 `atomic_write_verify` 直接寫,因為這個組合(frontmatter 欄位 + body 散文同一次原子寫)本來就不是 `cmd_set` 的能力範圍,不算「第二套寫入機制」,是用跟 `cmd_set` 內部一樣的兩顆原語(`atomic_write_verify`/`_vault_write_lock`)做 `cmd_set` 做不到的事。

已讀,無 finding。

## 問2:命名與錯誤處理

rc 語意、三態開關、略過旗標、治理帳事件、doctor 段寫法逐項跟鄰居核對,吻合:

1. rc 語意:`cmd_note_shape` docstring「有新違規 rc1,沒有 rc0;參數錯 rc2」與程式碼(`--diff` 格式錯 file: `scripts/lumos:24107`、終點找不到 file: `scripts/lumos:24124`)跟 spec S1「參數錯回 2」「block 模式回 1、只有『只列出』時回 0」同一形狀 — file: `scripts/lumos:24080`
2. warn 模式即使有發現仍回 0、只記 `warned` 事件:`return 0` 緊接在 `_gate_event_or_warn(root, "note-shape", "warned", ...)` 之後 — file: `scripts/lumos:24172`-`24174`,跟 spec「warn 只印並記 warned」一致
3. 略過開關只認字串 `"1"`:`LUMOS_SKIP_NOTE_SHAPE`(file: `scripts/lumos:24097`)、`LUMOS_SKIP_NOTE_AUDIT`(file: `scripts/lumos:24804`)、`LUMOS_SKIP_BOUND_TESTS`(file: `scripts/lumos:31044`)全部同一寫法,`LUMOS_SKIP_DRIFT_CHECK` 沿用同一命名與語意(`只認 1`)
4. gate 三態與設定檔鍵:`note_shape.gate`(file: `scripts/lumos:23511`)、`note_audit.gate`(file: `scripts/lumos:24208`)都是 `.lumos/config.json` 底下 snake_case 頂層鍵 + `.gate` 子鍵、值域 `block/warn/off`,`drift_check.gate` 跟這組同名同形(不是 `node_home.gate` 那組 `on/warn/off` 的舊三態)
5. 治理帳事件種類:`blocked`/`warned`/`skipped-env`/`skipped` 四個字串在既有多處出現(file: `scripts/lumos:23401`、`24099`、`24116`、`24130`、`24417`、`24433`、`24806`);`degraded` 這個 kind 也不是新造字,`delguard` 閘已經在用同樣語意(「判不了但看得見、不擋」)—— file: `scripts/lumos:25605`,附近 25616 行的註解「`"degraded": true, "reason": "timeout"|"error"`」字面上就是 spec §0「判不了的時候」那段要的語意
6. `理由少於 4 個字拒絕`:跟 note-audit 的 `略過` 理由檢查逐字同一門檻 `len(note.strip()) < 4` — file: `scripts/lumos:24857`
7. doctor 段名 `Z`:目前用過的段名到 `Y`(file: `scripts/lumos:2621` 附近),`cmd_doctor` 最後一段是 `F`(file: `scripts/lumos:2788`)、之後直接進總結列印,`Z` 沒有跟既有段名衝突,擺在總結前是合理的新增位置

已讀,無 finding(此問未發現跟鄰居不一致之處)。

## 問3:是不是第二種做法

### 3a `[when-…:…]` 跟 `[until:]`/`[retire:]`/`revalidate_when`/`valid_under` — F1(major)

### 3b `drift ack` 跟 `lint-waive`

兩者形狀確實不同:`lint-waive` 是單一 JSON 字典(`.lumos/lint-waivers.json`,key=指紋)— file: `scripts/lumos:21040`、`21429`;`drift ack` 提案是 append-only jsonl(`governance/drift-acks.jsonl`,key=內容編號+發現種類)。但這不是本專案「一件事兩套做法」的那種重複:既有的 note-audit 本來就有自己專屬的「略過」放行機制(判定檔 `kind: "略過"`,存在 `governance/note-verdicts/`,理由門檻同 4 字)— file: `scripts/lumos:24857`、`24877`,格式跟 lint-waive 也不同。也就是說「每個內容閘各自有一套貼合自己判定粒度的表態/放行機制」本來就是這個 repo 已經在用的模式(fingerprint 粒度用字典、逐行內容編號粒度用 jsonl/判定檔),drift-ack 選 jsonl+內容編號是跟 note-audit 那套同宗,不是額外發明。

已讀,3b 無 finding;3a 見下方 F1。

## 問4:落點(lands_in)

`Systems/存量漂移守衛`(新開)、`Systems/筆記內容閘`、`Systems/筆記內容審` 三個落點合理:

1. `Systems/筆記內容閘.md` 的 `responsibility` 明寫「管筆記內容的機械擋:提交前與推送前擋新寫的程式行號引用、沒寫來源的現況描述…以及兩層共用的『範圍裡新寫、終點還在的筆記行』抽取與行判定」,`about_code: scripts/lumos`——新 REVISIT 形狀擋(第一層)與 doctor E5 的 `[when-…]` 例外都物理落在這塊程式碼旁邊(E5 在 `scripts/lumos:1944` 附近,note-shape 主體在 `23511`-`24178` 附近),落這篇合理
2. `Systems/筆記內容審.md` 的 `responsibility` 明寫「不管新筆記行怎麼從 git 抽…不管形狀擋(第一層)」,`_note_audit_items` 在它管的範圍內(file: `scripts/lumos:24282`),spec §2.5 明寫「這是第二層 `_note_audit_items` 的一處改動,寫進 [[Systems/筆記內容審]]」,跟既有 `about_code` 覆蓋範圍一致
3. `scripts/lumos` 這一支檔本來就被好幾篇 Systems 節點以「各管一塊功能」的方式共同列進 `about_code`(例如 `Systems/筆記內容審.md`、`Systems/筆記內容閘.md` 的 `about_code` 都寫 `scripts/lumos`,而不是整篇互斥),表示這個專案「每支檔有家」的落地方式本來就允許同一支大檔案由多篇 Systems 節點依 `responsibility` 分區共管,`lumos drift` 開一篇新的 `Systems/存量漂移守衛` 管 check/scan/ack/exam 那塊,跟既有落地方式一致

已讀,無 finding。

---

## F1 `[when-…:…]` 跟既有回頭條件欄位(`revalidate_when`/`valid_under`)沒有機械劃清邊界,frontmatter 值裡的條件會被兩套機制都摸不到

severity: major
blocking: 是 — 不先定邊界,實作者要嘛把 `[when-…]` 的掃描範圍做成「連 frontmatter 值都掃」(等於讓機器悄悄開始評估 `revalidate_when`/`valid_under` 這兩個原本純人工判讀的欄位,沒有 doctor/audit 把關就變成新的行為),要嘛做成「只掃 body 行」(那麼寫進 `revalidate_when: 改到 [when-status:X=done] 時重驗` 的條件語法會被使用者以為機器在判、實際上永遠不會被判,是個沉默失效的死語法)——兩種猜法做出的系統行為不同,而且 spec 沒有給出判準讓實作者選對。

引句:「可放在任何筆記行上(建議只放 REVISIT 行,見第 5 點)」

1. spec 〈做法〉第 2 節第 1 點明寫 `[when-…:…]` 這套語法「可放在任何筆記行上」,只是「建議」放在 REVISIT 行,不是規則層面限定只能放那裡。
2. spec 第 2 節第 5 點的補救邏輯只覆蓋「非 REVISIT 的 body 行」:「非 REVISIT 行帶條件的照舊由第二層判」,並舉例「目前沒有 X」這種現況句。但這條補救走的是筆記內容審(第二層)的 `_note_audit_items`,而這支函式明確跳過 frontmatter:`if not ln.strip() or reg == "other" or i in struct: continue` — file: `scripts/lumos:24313`。`_notelines_regions` 把 frontmatter 除了 `summary:`/`decisions:` 以外的頂層鍵(含 `valid_under`/`revalidate_when`)一律標成 `"other"` 區塊(`cur = "summary" if k == "summary" else ("decisions" if k == "decisions" else "other")`)— file: `scripts/lumos:23541`。也就是說,第二層的「非 REVISIT 行照舊判」這條保護網,結構上就不涵蓋 `valid_under:`/`revalidate_when:` 這兩個 frontmatter 欄位——它們是最貼近「回頭條件」語意、作者最可能誤用 `[when-…]` 語法的地方,卻恰好是第二層完全不看的區域。
3. `valid_under`/`revalidate_when` 是既有 `COND_KEYS`(`scripts/lumos:13842`:`COND_KEYS = ("valid_under", "revalidate_when")`),語意就是「這個結論在什麼前提下才算數 / 改到什麼時候該回頭重驗」,跟 spec 這整篇計劃「把回頭條件改成機器能判的條件」的目標語意上高度重疊,但 spec 的〈PRIOR-ART〉段(spec 第 27 行)完全沒有提到這兩個既有欄位、也沒解釋為什麼不擴充它們而要另開一套 `[when-…]` 語法、以及兩者各自的適用邊界。
4. 結果是兩套「回頭條件」機制(既有的散文 `revalidate_when`/`valid_under`,人工判讀;新的 `[when-…]` 括號語法,機器判讀)在同一批筆記行上並存,而 spec 沒有講清楚一行只能屬於哪一套、混寫時誰贏。

## F2 `[when-status:<節點>=<值>]` 的值支援 `done|superseded` 這種管線分隔「任一值」寫法,跟既有 `[鍵:值]` 家族的單一值慣例不同源

severity: minor
blocking: 否 — 不影響閘擋不擋人這個結構性問題,只是語法解析要多寫一段 split;不會讓實作者做出壞系統或錯誤決定,頂多解析邏輯要自己想清楚沒有先例可抄。

引句:「值可寫 `done|superseded`(任一)」

1. spec 第 66 行自己宣稱這套語法「照既有標記的 `[鍵:值]` 單值形狀」,但緊接著第 70 行 `[when-status:<節點>=<值>]` 的值定義成可以寫 `done|superseded` 表示「任一成立」。
2. 檢查既有 `[鍵:值]` 家族(`[since:]`/`[until:]`/`[retire:]`/`[confirmed:]`/`[status:]`)沒有一個支援管線分隔的「多選一」寫法:`[status:...]` 的正則 `STATUS_REF_RE = re.compile(r"\[status:\s*([^\]]*)\]")`(file: `scripts/lumos:2933`)只把整個值當一個字串比對,合法值只有 `active` 或 `superseded` 其中一個(file: `scripts/lumos:2999`:「不是認得的值(只收 active / superseded)」),CLAUDE.md 表格裡的 `active|superseded` 是文件表格列舉兩個合法單值,不是「同一行可以寫兩個用 `|` 隔開」的語法。
3. `[when-status:...]` 的 `done|superseded` 是這個 repo 目前唯一一處在單一 `[鍵:值]` 括號裡用管線做析取的寫法,沒有姊妹欄位可以參照它的解析規則(要不要 trim 空白、大小寫、重複值怎麼辦等)。

---

不對齊共 2 條,其中 major 1 條。
最高 major,blocking 共 1 條。
