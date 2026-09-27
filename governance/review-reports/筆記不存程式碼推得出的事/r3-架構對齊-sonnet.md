severity: major

### F1 直呼 note-shape 私有函式,不走共用層
severity: major
blocking: 是 —— 引入跨層直呼:重用邏輯目前只有一種先例(`_nodehome_*` 共用層),這份設計改成讓新指令直接呼叫另一道閘的私有函式,兩者是不同的做法
引句:「所以第二層跟第一層看的是同一批行」
file: `scripts/lumos:23579`(`_ns_range_added` 定義)、`scripts/lumos:23500`(`_ns_regions` 定義)、`scripts/lumos:23793`與`scripts/lumos:23809`(兩支函式目前只被 `_note_shape_eval` 呼叫,唯一呼叫端)

理據:本 repo 現有的「跨閘共用邏輯」先例只有一種形狀——`_nodehome_*` 前綴的共用層(`_nodehome_golive`、`_nodehome_config`、`_nodehome_reader`…),被 `home check` 與 `note-shape` 兩道閘一起呼叫(例如 `_nodehome_golive` 在 `scripts/lumos:22943` 定義,`home check` 於推送範圍算法呼叫、`note-shape` 也呼叫同一支,見 `scripts/lumos:23982`)。而 `_ns_range_added`、`_ns_regions` 是 `_ns_` 前綴——這是 note-shape 自己的私有層,目前全庫只有 `_note_shape_eval`(note-shape 自己)呼叫它們,`home check`、`code-loop`、`lint-new` 都沒有跨進來用。這份設計要讓「第二層」(note-audit)直接呼叫這兩支 `_ns_` 私有函式,而不是先把它們提升成 `_nodehome_*` 那種共用層或另起共用前綴——這是本 repo 目前沒有的重用方式:不是「呼叫共用層」,是「呼叫另一道閘的內部實作」。若要對齊既有做法,應該先把這兩支函式改名/歸戶到共用層(比照 `_nodehome_*` 的做法),而不是讓 note-audit 直接伸手進 note-shape 的私有命名空間。

### F2 通過紀錄的資料模型是「內容指紋」與「治理帳」混出的第三種
severity: major
blocking: 是 —— 引入了本 repo 沒有的第二種(實為第三種)通過紀錄做法
引句:「只列判成脈絡(含申訴後降成脈絡)的內容編號」
file: `scripts/lumos:21446`(`_lint_waivers_add`:獨立檔、讀-改-寫上鎖、查詢是「目前字典裡有沒有這個 key」的緊湊當前狀態)、`scripts/lumos:29358`-`29394`(`_codeloop_read_from_ledger`:治理帳裡只認「該分支最後一筆」`passed`/`skipped` 事件,`last = ev` 逐行覆蓋,不做跨紀錄聯集)

理據:本 repo 目前兩種既有的「放行怎麼記」各自是一種完整模式:①新增告警閘(`lint-waive`)是獨立檔案 `.lumos/lint-waivers.json`,一條告警一個指紋,讀-改-寫上鎖(`_vault_write_lock`),查詢時只看「這個指紋現在字典裡有沒有」——是一份會被清點、會被提交、緊湊的當前狀態表;②代碼審(`code-loop`)是寫進共用治理帳 `docs/.governance-log.jsonl`,但讀取端只認「這個分支最新一筆 passed/skipped 事件」,不做歷史聯集。這份設計(做法第 55–67 行)把①的「一條內容一個指紋」的綁定顆粒度,搬進②的「寫進共用、append-only 治理帳」存放位置,而且要求 `check`(第 67 行)對「被推送頂端提交裡的治理帳」重新掃出「每一行是否被某一筆(不限最新一筆、不限哪個分支)通過紀錄涵蓋」——這是要在一份只會變大、不會收斂成當前狀態的帳本裡,對全歷史做聯集式成員檢查。既有兩種模式都不是這樣用:①有壓縮成當前狀態的機制,②只認最後一筆。這是專案裡沒有的第三種資料模型,而且設計文字本身沒有交代掃描範圍要不要設上限(對照 `_note_shape_doctor_lines` 的 `_NS_DOCTOR_SCAN_CAP = 200`,`scripts/lumos:23457`),跟既有「事後掃描要設上限」的先例也不一致。

（附帶:設計在 55–58 行有自己提出「讀頂端提交而非工作樹」有沒有先例的說法,查證後這個手法本身有精神先例——note-shape/home-check 家族本來就是「讀被檢查的那個版本」而不是工作目錄(例如 `_note_shape_config(_nodehome_reader(root, tip_where)(".lumos/config.json"))`,`scripts/lumos:23996`);但唯一既有的「治理帳讀取」先例(`_codeloop_read_from_ledger`)其實是直接讀檔案系統上的 `docs/.governance-log.jsonl`(工作樹路徑),不是用 git cat-file 指定某個提交去讀——兩邊都只是部分先例,設計文字把兩者混講成「有先例」,這點值得編排者自己再確認一次要照哪邊。）

### F3 lands_in 指到的節點,自己的 responsibility 明講不管這件事
severity: major
blocking: 是 —— 落點與「每支檔有家」鐵則(改到的每支檔都得先有家,節點只准寫自己家的檔)直接衝突,若不處理,落地時這批新程式碼會找不到家
引句:「- Systems/筆記內容閘」
file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:6`(responsibility 欄:「…不管程式檔歸屬(那是每支檔有家)、不管推送前 AI 審查員(第二層計劃)」)、`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:8`-`13`(about_code 已經列了 `scripts/lumos`、`scripts/hooks/pre-commit`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`——跟這份計劃第二層要落地/呼叫的檔完全重疊)

理據:計劃開頭欄位 `lands_in` 指到 `Systems/筆記內容閘`(r3-work.md 第 10–11 行),但這篇節點是第一層(note-shape)上線時剛開的家,它的 `responsibility` 欄第一句就寫明它「不管…推送前 AI 審查員(第二層計劃)」——字面上排除了這份計劃要做的事。而它的 `about_code` 又已經列了 `scripts/lumos`、兩支 hook、`ci.yml` 這四支檔,跟第二層要新增程式碼、要在 pre-push/`ci.yml` 掛呼叫的檔完全重疊。照「每支檔有家」的鐵則(節點只准用反引號寫自己家的檔;改到的每支檔都得先有家),第二層新寫的那部分 `scripts/lumos` 程式碼、hook 裡新增的呼叫段落,現在的家不能是這篇——它自己說了不管。計劃裡沒有交代要開一篇新的 Systems 節點,還是要順手把這篇的 responsibility 改寫掉那句排除語;兩者選一都行,但目前 `lands_in` 跟目標節點自己的宣告是矛盾的,照現狀落地會讓這批新碼變成沒有家、被 home check 擋下。

## 四問逐答

**1. 分層與依賴方向**:新指令(`note-audit`)規劃直接呼叫 note-shape 的私有函式 `_ns_range_added`、`_ns_regions`(F1),這兩支函式目前是 note-shape 自己的內部實作,不是本 repo 既有的跨閘共用層(`_nodehome_*`)。除此之外,`check` 子命令「另開一支平行呼叫、跟 home check 同形狀」(做法第 67 行)這點是對的:實測 `scripts/hooks/pre-push` 裡 `home check --diff` 與 `note-shape --diff` 就是同一個 `_hrange` 迴圈裡背靠背呼叫(pre-push 第 210–226 行左右),`check` 照樣掛在那裡沒有問題。誰呼叫誰的方向(hook → 新指令、新指令 → 共用層)大致對,問題只在「共用層」那一段名不正——見 F1。

**2. 命名與錯誤處理**:`.lumos/config.json` 的鍵名 `note_audit.gate` 與既有 `note_shape.gate`、`node_home.gate`、`lint_new.gate` 同一種叫法(`<閘名>.gate`,見 `_note_shape_config` 於 `scripts/lumos:23479`);`gate` 值域 `block/warn/off` 與 `_NOTE_SHAPE_GATE_VALUES`(`scripts/lumos:23456`)一致;doctor 在非 block 時印一行提醒,照抄 `_note_shape_doctor_lines`(`scripts/lumos:23877`-`23880`)的先例,沒問題;`_gate_event` 通用寫入器與「登記進既有閘名單」(做法第 66 行)也對上了 `_KNOWN_GATES` 的機制(`scripts/lumos:6599`-`6615`、`scripts/lumos:898`-`902`)。唯一沒把握的是「skip」的事件種類:做法第 5 點只列了「passed / skipped / blocked」三種,但第 7 點同時要處理「作者顯式 `note-audit skip`」跟「`LUMOS_SKIP_NOTE_AUDIT=1` 環境變數跳過」兩種不同情境——既有鄰居對這兩種情境是分開命名的(`code-loop skip` 子命令寫 `kind="skipped"`,`scripts/lumos:30992`-`30994`;而 note-shape 的環境變數跳過寫的是不同的 `kind="skipped-env"`,`scripts/lumos:23955`-`23957`)。這份設計沒說清楚環境變數那條路要不要沿用 `skipped-env` 這個既有區分,這點判不準,標 ⚠ 交編排者確認。

### F4 環境變數跳過的事件種類名沒交代清楚
severity: minor
blocking: 否 —— 判不出是不是真的不一致(有可能設計本意就是沿用 skipped-env,只是文字沒寫全)
引句:「同第一層)。模型限流、服務中斷時走 skip」
file: `scripts/lumos:23955`-`23957`(`LUMOS_SKIP_NOTE_SHAPE` 寫 `kind="skipped-env"`)、`scripts/lumos:30992`-`30994`(`code-loop skip` 子命令寫 `kind="skipped"`)

**3. 第二種做法**:核心問題見 F2——通過紀錄「逐行涵蓋、寫進治理帳」把 lint-waive 的「內容指紋」綁定顆粒度,搬進 code-loop「寫進共用治理帳」的存放位置,而讀取端(`check`)還要求對治理帳做跨紀錄聯集式成員檢查,這是既有兩種做法(獨立放行檔的當前狀態表 vs. 治理帳只認最後一筆)都沒有的第三種。至於「讀頂端提交裡的檔而不讀工作樹」本身,精神上有先例(note-shape/home-check 家族一律讀「被檢查的版本」,見 `scripts/lumos:23996`),但唯一既有的治理帳讀取先例(`_codeloop_read_from_ledger`,`scripts/lumos:29358`)其實是讀工作樹上的檔案路徑,不是指定提交讀 blob——這半個「先例」講得不夠準,值得編排者自己核一次。

**4. 落點合不合理**:不合理,見 F3——`lands_in` 指到的 `Systems/筆記內容閘` 節點,它自己的 `responsibility` 欄明講不管「推送前 AI 審查員(第二層計劃)」,而且 `about_code` 已經列了這份計劃要動的同一批檔案。計劃要嘛開一篇新的 Systems 節點,要嘛先把那篇的 responsibility 改寫掉排除語,兩者現在都沒寫進計劃裡。

不對齊共 4 條,其中 major 3 條。
