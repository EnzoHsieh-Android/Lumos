severity: major

固定席筆記:這次派工詞尾端沒有 hook 附上的固定席筆記,所以沒有「不影響」可判。

我的鏡頭是資源與時序。r1 資源併發席的 R1(只看新行還是前提變就擋)、R6(搜尋預設求值)、R9(寫帳矛盾)和 R2 的「沒有預算」一半,v2 都補上了:改接 `_drift_probe_check` 的候選篩選與轉變判定,搜尋改成只看靜態標記,併發節改寫成只寫治理帳。R2 的另一半(重算器在 gate 裡的資料來源與失敗語意)沒補上,見 R2R2。新版新增的段落也帶出新洞,如下。

**R2R1**
severity: major
blocking: 是——照字面實作,「判不了」會同時有兩種相反的行為,而且不可解的欄位沒有逐條出口。
- 輸入:欄位指到非 Python 檔、程式組出來的集合,或超大的 `.py`(例如幾十 MB 的產生檔)。
- 〈欄位 v1〉表格與 S5 說「判不了」就不擋。
- 〈判不了〉那條卻說「照存量漂移檢查既有的處理……不另訂」。既有處理正好相反:`cmd_drift_check` 的 docstring 寫判不了「算要處理——放行等於一條繞過的路」(`scripts/lumos:29778`)。印給人的字樣是「判不了就放行等於一條繞過的路,所以算要處理」(`scripts/lumos:30579`)。
- 這種判不了只有 `LUMOS_SKIP_DRIFT_CHECK=1` 一條出口。`drift ack` 只作用在「要處理」的發現,判不了的項目走不到它(`scripts/lumos:30579` 的提示只給單次跳過)。實務隱患節卻寫「針對某一條用 `drift ack`」,對這種項目做不到。
- 括號裡的三件事行為本來就不同,spec 把它們併成一條:
  - git 逾時:算要處理,擋。
  - 預算用完:算要處理,擋。
  - 淺複製:整道檢查靜默跳過、rc 0(`scripts/lumos:26282`、`scripts/lumos:26287`)。
- 「嚴格判定沿用它的設定」也指不到東西:嚴格度是寫死的,沒有設定值。
- 新的求值器沒說大檔怎麼辦。既有程式有兩層防線,spec 一層都沒提:
  - `ast.parse` 會丟 MemoryError、RecursionError,既有程式接住並回「判不了」(`scripts/lumos:28108`)。
  - 超過 4MB 的 blob 不用 ast,改文字抽定義(`scripts/lumos:29868`)。
- 實作者得自己決定:大檔、深巢狀、非 Python 到底算擋還是放。S5 要「不擋」,現有出口卻是「擋」,最壞的結果是任何碰到那支檔的推送都被擋、只能整道略過。
- 引句:「照存量漂移檢查既有的處理(git 逾時、淺複製、預算用完時的嚴格判定沿用它的設定),不另訂。」
- 佐證行 file: `scripts/lumos:29778`、`scripts/lumos:30579`、`scripts/lumos:26282`、`scripts/lumos:28108`、`scripts/lumos:29868`

**R2R2**
severity: major
blocking: 是——共用重算函式放進推送閘,資料來源、上限和預算三處語意都沒定,實作者必然猜。
- 現有 doctor N 的重算是 `cmd_doctor` 裡的內嵌迴圈,不是函式。
- 它用 `os.walk(repo_root)` 掃工作目錄(`scripts/lumos:3040`)。推送閘判的是被推送的頂端和起點兩個提交,不是工作目錄。CI 的工作目錄也未必等於被推的提交。
- 閘要比「起點吻合、終點不吻合」,所以每個標記要在起點和終點各重算一次,各讀至多 4000 支、40MB 的檔。spec 沒說抽出來的函式要改成吃樹(提交或 disk),也沒說兩份讀取共用快取。
- 「受總時間預算管」做不到細粒度。預算只在兩次呼叫之間檢查(`_DriftProbeTree._over()` 在 `scripts/lumos:28311` 的 `_read` 開頭)。`cre.findall(body_)`(`scripts/lumos:3055`)沒有任何中斷點。
  - 使用者寫的 `re=` 若是災難性回溯,例如 `(a+)+$`,pre-push 就卡死,預算管不到。
- 上限超過時,doctor 只是丟一個軟提醒(`scripts/lumos:3049` 的 `RuntimeError`,收進 `_bad`)。進了閘就依 R2R1 變成「判不了=擋」。
  - 一個早年寫的 `in=**/*.py` 標記,repo 長到超過 4000 支檔後,之後每個碰到符合檔的推送都被擋。
  - spec 沒給「上限超過」的處理。
- 引句:「重算受存量漂移檢查的總時間預算管,不再每個標記各自無上限地掃整個 repo。」
- 佐證行 file: `scripts/lumos:3040`、`scripts/lumos:3049`、`scripts/lumos:3055`、`scripts/lumos:28311`

**R2R3**
severity: major
blocking: 是——W1 範本需要的路徑和值沒有取得方式,也沒有成本上限,實作者要自建一條提交前的全庫符號解析。
- W1 的範例範本是 `[count:app/config.py::MODEL_VARS=4]`,要印出這串就得知道三件事:
  - 符號定義在哪支檔。
  - 它的值是多少。
  - 該用 count、value 還是 lives 哪一種。
- 但條文只寫「把那個名稱填進範本」,沒說另兩項從哪來,也沒說「程式符號」怎麼判。
- 唯一現成做法是讀全庫程式檔:
  - `_DriftProbeTree.corpus` 讀全部程式檔(`scripts/lumos:28297` 一帶)。
  - 或 `build_code_haystack` 用 `os.walk` 全讀(`scripts/lumos:4739`)。
  - 上萬支程式檔的 repo 放在每次 `git commit` 的提交前掛鉤上,沒有預算、沒有 deadline。
- `_note_shape_eval` 目前的提醒路徑只在 `--staged` 且失敗時整批丟掉(`scripts/lumos:25570`)。沒有時間上限,卡住就卡住提交。
- 輸出也沒有上限。既有的否定現況句提醒是「全部印出,不設上限」(`scripts/lumos:25514`)。
  - W1 比它觸發頻繁得多,因為幾乎每條新寫的 WHY、RULE、PITFALL 都會用反引號提到名稱。
  - 一次提交若新增幾十行,等於幾十份多行範本加速查表灌進 AI 的上下文。
- 引句:「新寫的 WHY、RULE、PITFALL 行用反引號提到程式符號,又沒帶任何依賴欄位 → 提醒」
- 佐證行 file: `scripts/lumos:25514`、`scripts/lumos:25570`、`scripts/lumos:4739`、`scripts/lumos:28297`

**R2R4**
severity: minor
blocking: 否——兩種做法都能運作,只是「不溯及既往」承諾和 S7 對舊標記的處理互相矛盾,需要人決定。⚠ 交編排者:消費專案裡有多少篇已經帶 HTML 數量標記,我查不到。
- 輸入:舊筆記裡已經有 `<!--lumos:count=N re=… in=…-->`。doctor N 自 2026-08 起就存在,doctor 對它只是「提醒,不擋」(`scripts/lumos:3017`)。
- 〈欄位 v1〉說存量漂移檢查現在也要重算它,「起點吻合、終點不吻合 → 擋」。`drift_check.fields` 預設是 block。
- 結果:沒有人新寫任何依賴欄位,只因為升級工具,舊標記就從提醒變成硬擋。
- 〈不溯及既往〉寫「沒寫欄位的筆記(所有舊筆記)完全不受影響」,S1 寫「沒有寫任何依賴欄位」。標記算不算欄位沒定義,這兩條有歧義。
- 引句:「欄位檢查只看寫了欄位的行:沒寫欄位的筆記(所有舊筆記)完全不受影響。」
- 佐證行 file: `scripts/lumos:3017`

**R2R5**
severity: minor
blocking: 否——最差是 CI 後盾在預設淺複製下靜默不生效,本機推送前掛鉤仍在。
- 輸入:消費專案的 CI 用 `actions/checkout` 預設的 `fetch-depth: 1`。
- 實務隱患節寫跳過後「CI 照擋」,並把 CI 當成工具鏈也擋的後盾。
- 但 `lumos drift check` 在淺複製下直接印「這次不查」並 rc 0(`scripts/lumos:26282`、`scripts/lumos:26287`)。
- `_drift_gate_doctor_lines` 只檢查 CI 檔裡有沒有 `drift check` 這串字(`scripts/lumos:30918`)。它不像 note-shape、note-audit 那兩道一樣,用 `_ci_jobs_calling_without_full_history` 提醒 CI 沒抓完整歷史(對照 `scripts/lumos:25711`、`scripts/lumos:31434`)。
- 所以新欄位的 CI 後盾在這種專案上靜默失效,doctor 也不會講。
- spec 沒說新閘要不要補這個 doctor 提醒。
- 引句:「單次跳過 `LUMOS_SKIP_DRIFT_CHECK=1`(既有,會留帳、CI 照擋)」
- 佐證行 file: `scripts/lumos:26282`、`scripts/lumos:30918`

**R2R6**
severity: minor
blocking: 否——CI 的主線推送步驟事後仍會抓到,只是併發節描述的機制不成立。
- 輸入:兩條互不衝突的分支,A 把 `MODEL_VARS` 從 4 改 5,B 新增 `=4` 的欄位。各自對自己的頂端判都綠。
- 〈實務隱患·併發〉說「後推的人 rebase 後重算」。透過 PR 的 merge 按鈕併入時沒有 rebase,而且存量漂移檢查在 CI 只跑 `push` 事件(`.github/workflows/ci.yml:161`)。
  - 所以第二個併入的那次主線推送才會事後擋,主線先紅。
  - 之後的推送起點已經不吻合,依 S3 不再擋,只剩 doctor 列出。
- 引句:「兩個推送各自對自己的頂端判,後推的人 rebase 後重算。」
- 佐證行 file: `.github/workflows/ci.yml:161`

**R2R7**
severity: minor
blocking: 否——S4 與表格同一格互相矛盾,實作者看 S4 就會做對。
- 〈欄位 v1〉表頭寫「只看這次改到 `路徑` 那支檔的欄位」。
- 同一格又要求「這次新寫的欄位在終點就不吻合 → 擋」。新寫欄位指到的檔往往這次沒改。
- 既有探針的做法是「起點沒有同一條的(新寫或改了條件)一律是候選」(`scripts/lumos:28557`)。
- 照表頭字面實作,新寫但指到未改檔的欄位寫錯會漏過去,S4 就失效。
- 引句:「判過時(推送時,只看這次改到 `路徑` 那支檔的欄位)」
- 佐證行 file: `scripts/lumos:28557`

## 逐節結論

- frontmatter、依據、PRIOR-ART、RETIRE-IF、現況、設計原則、前綴表:已讀,無 finding。
- 引用核對:`〈天花板〉第 2 條`、`〈回退〉`、`〈分期〉`、`〈讓 AI 知道該寫什麼〉第 4 點`、`〈欄位 v1〉`都找得到對應段。
- 〈欄位 v1〉:R2R1、R2R2、R2R4、R2R7。
- 〈寫法提醒〉:R2R3。W2、W6 是純字串比對,成本可忽略;W4 走既有新增行那條路。已讀,無其他 finding。
- 〈讓 AI 知道該寫什麼〉:改檔前 hook 不動,所以沒有「hook 多附速查表」的成本。`scripts/hooks/claude/impact-hook.py` 的 `EXCLUDE_PATH_CONTAINS` 含 `/docs/`,確認筆記不會觸發。速查表只在提交時多印一次,成本在 R2R3 的輸出量裡。
- 〈按需載入〉:已讀,無 finding。`cmd_search` 主迴圈本來就逐篇 `read_text`,新增篩選只是字串判斷,不求值。行模式 `--top 0` 全給,屬使用者主動要求。
- 〈不溯及既往〉:R2R4。
- 〈實務隱患〉:R2R5、R2R6。
- 〈驗收條款〉:S1 到 S19 的編號都有 `[test:]` 或 `[manual:]`。S5 與既有判不了語意衝突(R2R1),S7 的共用函式沒定義資料來源(R2R2)。
- 〈回退〉、〈合約候選〉、〈已裁〉、〈不做〉、〈天花板〉:已讀,無 finding。

## 實務隱患逐類(我的鏡頭)

- **併發/時序**:有隱患,見 R2R6。治理帳寫入沿用既有的 `_gate_event_or_warn`,spec 已承認,r1 的 R9 已補上。
- **大 repo 成本**:
  - 推送閘本身:沿用既有 `_drift_tree_env` 的批次讀取,欄位掃描不增加讀取量,沒問題。
  - HTML 標記重算:有隱患,見 R2R2。
  - W1:有隱患,見 R2R3。
  - 搜尋:無隱患,因為 `cmd_search` 本來就逐篇讀全部筆記。
- **git 呼叫逾時、判不了時擋或放**:有隱患,見 R2R1。
- **淺複製 CI**:有隱患,見 R2R5。
- **改檔前 hook 成本**:無,因為 spec 明確不動 hook。
- **資源與長駐、注入**:無。不開程序、不加連線,搜尋輸出同現在。

最高嚴重度:major,blocking 3 條
