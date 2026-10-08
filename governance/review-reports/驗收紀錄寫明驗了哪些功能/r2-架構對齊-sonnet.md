severity: major

(對照 repo 為 negguard 快照下的 scripts/lumos,以下 file 行號皆指該檔)

## 四問

**1. 分層與依賴方向。** 大方向對齊:共用函式 `_verification_system_targets(env, rel, n)` 的簽名與底線前綴跟鄰居 `_suggest_systems_for_orphan(env, rel, n)`(scripts/lumos:805)一致;把 doctor 3/4 與 `sync-verified-by` 兩份重複的判法收成一份,方向對。寫入端走既有 `cmd_append`(跟 plan_refs 在 `cmd_new` 的寫法同,scripts/lumos:19200)也對。`remove` 塞專屬提醒:`_cmd_remove_locked` 現況對特定 key 只有 `about_code` 一條分支,而且是「比對鍵」資料層(scripts/lumos:17820 一帶),沒有任何「刪完印語意後果提醒」的先例;相鄰的危險情況(整欄刪 verified_by)鄰居的做法是硬擋 rc2(scripts/lumos:17883 `_cmd_remove_scalar`),不是印提醒。寫入層開始知道 doctor 3/4 的讀取語意,屬輕度跨層,見 F4(minor,⚠)。真正的第二種做法在連結嚴格判(F1)。
**2. 命名與錯誤處理。** 欄位名 `system_refs` 與 `plan_refs`/`verified_by` 同族,沒問題。寫壞自己報(照 doctor 4/4 對 plan_refs 斷鏈,scripts/lumos:1514-1523)對齊;寫入失敗用「提醒:筆記建好了,但…」+ rc2(scripts/lumos:19202、19211)對齊;`warn` 計 issue、`warn_soft` 不計(scripts/lumos:1361、1383,精神同 2550 的「不計入問題數」)用法對。不齊處:`無` 的判法與門檻(F2)、`[]` 的語意與 `aliases: []` 先例相反(F5)。
**3. 第二種做法。** 有兩處:每項嚴格判連結等於在 doctor 內重寫了 `build_typed_index` 已有的「整值恰為一個 wikilink、path 式不 fallback 到 stem、同名多候選報 ambiguous」那套(F1,major)。`無 <理由>` 沒有重寫 `_slot_replacement_err`,但另立了門檻(F2)。「跳過 stale/fail/superseded 只留一份」不實,E1 還留一份(F3)。
**4. 落點。** lands_in 兩篇(lumos-cli-read / lumos-cli-write)、共用函式放 doctor 一帶、`LIST_KEYS` 登記(scripts/lumos:17105)、不進 `LINK_KEYS`/`TYPED_EDGE_FIELDS` 的收窄理由都站得住。唯一疑問:新的「功能側多掛」軟提醒放在 3/4,而同家族的「功能的 verified_by 指到不該指的紀錄」現在住在 Check E1(scripts/lumos:2133-2147),見 F6(minor,⚠)。

## F1 每項嚴格判連結是在 doctor 裡第二次實作 build_typed_index 的連結分類
severity: major
blocking: 是
引句:「而且連結有寫路徑時路徑要跟解析結果一致」
file: `scripts/lumos:737-790`(build_typed_index:恰為單一 wikilink 才收、否則進 scalars;path 式「不 fallback 到 stem」查不到進 ghosts;無路徑同名多候選進 ambiguous、嚴禁靜默指第一篇;註解自述不走 env.resolve)
1. 既有鄰居已對 verified_by/plan_refs/related 這三個 frontmatter 連結欄位定義了一套完整分類(scalars / ghosts / ambiguous / path 式不救援)。計劃第 38 行(做法 1 第二點)用 `env.resolve` 加「路徑要一致」「無路徑落別的資料夾算寫壞」再造一套,規則並不相同:鄰居對無路徑多候選報 ambiguous,計劃只在解析結果「不在 Systems/」才報,Projects/A 與 Systems/A 同名時 env.resolve 會挑誰、與 ambiguous 判法會不會分歧,計劃沒講。
2. 這會讓同一個 frontmatter 連結值在兩處得到不同判定,日後修一邊漏另一邊,正是「第二種做法」。
3. 建議:把 build_typed_index 內「單一 wikilink → (rel | ghost | ambiguous | scalar)」那段抽成一支小函式(不必把 system_refs 加進 TYPED_EDGE_FIELDS,範圍收窄照舊),`_verification_system_targets` 呼叫它再加「落在 Systems/」;或在計劃明寫為何不能共用並承諾「同名多候選」的處置與 ambiguous 一致。

## F2 `無 <理由>` 的判法另立門檻,沒有對齊既有「至少 N 字」的判法
severity: minor
blocking: 否
引句:「②整份清單只有一項、是 `無` 加至少 4 個字的理由」
file: `scripts/lumos:3894-3899`(_slot_replacement_err:`startswith("無")` 且後面非空即收,不設字數)、`scripts/lumos:25955`、`scripts/lumos:26052`(`_NODEHOME_RESP_MIN_CHARS = 10`、`_nodehome_resp_ok`:至少 N 字且要有實字)
1. 沒有整個重寫 `_slot_replacement_err`(它同時收 `[[節點]]`,不能直接套),這點對齊。但「無 + 理由」的字面解析(`startswith("無")`,`無理由`無空格也收)與「理由夠不夠實」本專案已有兩套:格子是「非空」、節點負責範圍是「≥10 字有實字」。計劃第三套「≥4 字」,理由沒說。
2. 建議:挑一套(多半是 `_nodehome_resp_ok` 那種「有實字」判法換較小門檻),抽成 `無`-理由小 helper 讓兩處共用;或在計劃寫明為何不沿用格子的「非空即可」。

## F3 「跳過狀態只留這一份」與現況不符,E1 還有第三份
severity: minor
blocking: 否
引句:「跳過哪些狀態也只留這一份」
file: `scripts/lumos:1488`(doctor 3/4)、`scripts/lumos:15855`(sync-verified-by)、`scripts/lumos:2147`(Check E1:`vst in ("stale", "fail", "superseded")`)
1. 現況是三份同樣的三元組,計劃只收 3/4 與 sync(外加孤兒推薦,它目前是 n.targets 加 resolve,並沒有這個跳過集),E1 那份留著。doctor 註解(scripts/lumos:1481-1487)自己說 E1 與 3/4 要「位一致」,正是會漂的地方。
2. 建議:共用函式外另露出一個常數或小函式 `_VERIFICATION_DEAD_STATUSES`(或 `_verification_is_dead(env, rel)`),三處都用;至少把計劃字句改成「3/4 與 sync 只留這一份,E1 仍有一份、已列入同步」。

## F4 `remove` 刪光最後一項時印專屬提醒:寫入層知道 doctor 讀取語意,且沒有先例
severity: minor
⚠
blocking: 否
引句:「對驗收紀錄的 `system_refs` 這樣刪光時,`remove` 另印一句提醒」
file: `scripts/lumos:17805-17875`(cmd_remove / _cmd_remove_locked:除 about_code 的比對分支外沒有 per-key 的語意提醒;成功只印 `✓ remove …`)、`scripts/lumos:17883-17895`(危險的整欄刪除在鄰居是硬擋 rc2)
1. 提醒的內容(「回到從正文推、指路連結又被要求反向登記」)是 doctor 3/4 的讀取語意,放進通用寫入指令等於寫入層依賴讀取層的規則,日後 3/4 判法改了這句會變成過期說明,且沒有守衛綁它。鄰居對「刪了會出事」的處置是擋住並指路,不是事後提醒。
2. 判不準的部分:提醒本身無害、只印不改 rc,屬輕度;若要照鄰居做法,可改成「刪最後一項時擋下、指向 `無 <理由>`」,或把提醒移到 doctor 3/4(紀錄沒宣告又正文有 Systems 連結時,advice 說「想宣告沒驗任何功能請寫 無 <理由>」,這句計劃本來就要放進 NEW_HINT)。
3. 建議至少在計劃寫明提醒放在哪個函式、由哪條條款(S9)綁測試,並說明為何不像 `_cmd_remove_scalar` 用擋下。

## F5 `[]` 判寫壞,與計劃自己引用的 `aliases: []` 宣告制先例語意相反
severity: minor
blocking: 否
引句:「宣告優先、沒宣告才推」在本 repo 的近似先例是 `aliases: []` 宣告制
file: `scripts/lumos:5921-5928`(`aliases: []` = 明示判過、合法)、`scripts/lumos:17155`(`[]` 是合法空清單)
1. PRIOR-ART 引 aliases 當先例,但那邊空清單是合法的「我判過、沒有」;計劃空清單算寫壞、要改寫 `無 <理由>`。理由(remove 刪光後鍵消失、空清單用指令到不了)計劃有交代,但 PRIOR-ART 一行沒標「此處刻意相反」,下個讀者會以為同款。
2. 建議:PRIOR-ART 補半句「與 aliases 相反:`[]` 在此算寫壞,因為 remove 會連鍵刪掉、`[]` 無指令可達」。

## F6 「功能側多掛」軟提醒放 3/4,同家族的檢查住在 E1
severity: minor
⚠
blocking: 否
引句:「有 N 篇功能筆記多掛了沒宣告它的驗收紀錄」
file: `scripts/lumos:2133-2147`(Check E1:功能的 verified_by 指到 stale/fail/superseded 驗證 = 死背書,軟提醒、不計 issue)
1. E1 已經是「功能那側 verified_by 指到不該指的驗收紀錄」的家;新檢查語意是同一家族的另一種不該指(指到沒宣告它的紀錄)。放在 3/4 就是同一類問題兩個落點。判不準:3/4 是「驗收紀錄 → 功能」方向,新檢查在 3/4 掃功能側也順手;但改法文字(`lumos remove <功能> verified_by`)與 E1 的建議動作重疊。
2. 建議:計劃說明為何不併進 E1,或把它掛 E1 段落並共用 E1 的 vst 判法(連到 F3)。

不對齊共 6 條,其中 major 1 條
