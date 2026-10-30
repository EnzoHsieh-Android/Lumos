severity: major

審查範圍:第 2 版快照 `r2-snapshot.md`,對照 `scripts/lumos` 與 `.lumos/` 底下既有做法。

## 1. 分層與依賴方向
對齊,有一處待定的小事。

- 讀舊檔清單走「讀宣告的同一版」,沿用 `_trusted_decl_ref`(`scripts/lumos:57387`)和 `_lens_trusted_ref`(`scripts/lumos:57364`)。沒有主線時分級照讀起點、派工鏡頭不讀。這跟 `no_mainline_reads_base` 的既有語意一致(`scripts/lumos:57387-57395`),沒有跨層直呼。
- 三處(推送前分級、派工鏡頭、代碼審判定)共用一支判定函式,方向與 `_arch_targets_at`(`scripts/lumos:57408`)被三處共用的做法一樣。
- 代碼審說明行加進 `_arch_target_check_lines` 的 `lines.append(...)`(`scripts/lumos:57631-57654`),doctor 行加進 `_arch_target_doctor_lines` 的 (清單行, 提醒行) 回傳(`scripts/lumos:57494-57520`)。落點與形狀都對齊。
- ⚠ 交編排者:doctor 既有讀的是 `HEAD` 版(`_arch_targets_at(root, "HEAD")`),快照第 8 點的 Konsist 讀工作目錄版,doctor 清單摘要讀哪一版快照沒寫。這是規格缺口,不是結構問題。

## 2. 命名與錯誤處理
大致對齊,有兩條 minor。

- 讀不懂時「整份不用、全照鄰居審」的處置,跟 `_arch_targets_config` 的 `tail` 慣例一致(`scripts/lumos:57312`)。畢業遇到「任一版讀不懂就整批不畢業」也同向,更保守。
- 寫檔走 `_write_lf`(`scripts/lumos:28496`),跟 `cmd_new`(`scripts/lumos:30766`)新建節點同一原語,對齊。

severity: minor
blocking: 否
- 快照第 3 點寫「寫幾個新檔、在設定檔加一鍵,不跟其他指令共用狀態」。但 `.lumos/config.json` 是所有指令共讀的共用檔。`_write_lf` 的說明明寫讀改寫要由呼叫端拿鎖(`scripts/lumos:28496-28510`),而既有的讀改寫都包在 `_vault_write_lock`(例如 `scripts/lumos:14165`、`scripts/lumos:16001`)。
- 設定檔既有的寫入只有 `init` 的「檔存在就不碰」(`scripts/lumos:32993-33000`),沒有任何「改既有設定檔」的先例。產生器是第一個,快照卻沒講上鎖。
- 引句:「寫檔走 lumos 共用的 `_write_lf`(先寫暫存再替換);先寫新檔、設定檔最後寫,設定檔失敗就刪掉這次新建的檔。」

severity: minor
blocking: 否
- 既有說明行的措辭是「本次審查仍用起點版,下次推送才生效」,是固定句。新增的三句帶變數,這點本身可以接受。但快照第 7 點同時要印兩種說明時的順序和合併方式沒定。既有函式是一條 `if changed` 單句(`scripts/lumos:57652-57653`),沒有多句並存的先例。
- 引句:「宣告或目標節點有改時照舊印「下次推送才生效」;第一行的檔數標明「含畢業 N 支」。」

## 3. 第二種做法
不對齊,有一條 major。

severity: major
blocking: 是
- 專案裡「這批檔照鄰居審」已經有一種宣告方式:`arch_targets` 的 `{"path":…, "node":"none"}`,第一條命中算數(`scripts/lumos:57307-57335`)。快照新增舊檔清單 `.lumos/arch-legacy.txt`,也是「列了就照鄰居審」。同一件事現在有兩條宣告路,各有不同的比對語意:`none` 是萬用字元樣式、清單是字面整行。
- 兩者互動(清單與 `none` 同時命中、清單只在「落在目標節點範圍內」才算)只靠快照自己的規則維持。接手的人要在兩套之間猜該寫哪一套。
- 檔案格式也是第二種。`.lumos/` 底下既有的狀態與清單檔全是 JSON 或 JSONL:`.lumos/config.json`、`.lumos/lint-waivers.json`(`scripts/lumos:38679-38698`,帶 by、reason、ts)、`.lumos/lint.json`、`.lumos/security-approvals.jsonl`(`scripts/lumos:8539`)、`.lumos/vendored.json`(`scripts/lumos:31991`)。
- 唯一的「從 git ref 讀」函式 `_json_at_ref`(`scripts/lumos:62804`)和 `_lumos_config_at_ref`(`scripts/lumos:57337`,雖有 `rel` 參數,底層仍只讀 JSON)都只認 JSON。清單檔要另寫一套純文字的「讀某版本」,還要有自己的 BOM、編碼、換行處理。
- 同樣的「列出豁免」,專案已有帶理由與簽名的 `lint-waivers.json`,也有 `governance/anchor-baseline.json`(`scripts/lumos:33962`)。快照借用的 detekt baseline 本身是外部先例,不是本專案的做法。
- 快照 r1 折入時已逐項說明為何不用 `none` 宣告:500 條上限、方括號被當萬用字元、改名掉出、doctor 每死行一行、Konsist 要解析 JSON。這些理由成立。但它只證明「現行機制不夠」,沒回答第二種做法的代價:沒有說明 `none` 宣告與清單何時選哪個,也沒有說明為何不是擴充 `arch_targets`(例如加字面欄位)。
- ⚠ 這條是否放行是設計取捨,請編排者裁。至少要在規格裡寫清兩者分工和優先序。
- 引句:「舊檔清單:`.lumos/arch-legacy.txt`(新增),一行一個 repo 相對路徑;列在上面、又落在某個目標節點範圍內的檔,照鄰居審。照字面整行比對,不當萬用字元。」

另有兩處不另列 major:

- 產生器改寫既有 `config.json` 時「整檔重寫成兩格縮排、中文不跳脫」(快照第 3 點)。這是 `init` 沒有、其他寫設定檔處也沒有的第二種寫法,只是副作用。
- 開關資料檔 `scripts/templates/android-arch-target.md` 登記進 `_VENDORED_TREE_FILES`(`scripts/lumos:31963`),跟既有 `scripts/templates/` 範本做法一致,對齊。

## 4. 落點
大致合理。

- 同一件事寫兩個家:生成器說明寫新節點 `Systems/android-arch-template`,畢業與清單讀法寫既有的 `Systems/arch-alignment-lens`。這跟「架構對齊怎麼選基準」同屬一篇的分法合理。
- 現況:`arch-alignment-lens` 的 about_code 已含 `scripts/lumos`,畢業判定函式和三處呼叫落在這裡,沒問題。
- ⚠ 清單檔 `.lumos/arch-legacy.txt` 的格式與讀法,快照只講進 `arch-alignment-lens`。它本質上跟 `arch_targets` 同為宣告檔,但讀法完全不同,建議在 `arch-alignment-lens` 明寫「兩種宣告的分工」,呼應第 3 問的 major。
- `Systems/android-arch-template` 在會談目錄與凍結提交都找不到,是新開節點,符合快照寫的「新開一篇當它的家」。

不對齊共 3 條,其中 major 1 條。(minor 的兩條在第 2 問,major 的一條在第 3 問。)
