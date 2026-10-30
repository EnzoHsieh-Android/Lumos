severity: major

## 1. 分層與依賴方向:對齊(有一處待補說明)

- 畢業判定沿用共用的可信版本讀法,沒有另起一套。
  - 計劃寫「沿用既有的可信版本讀法」。對照 `scripts/lumos:57387`(`_trusted_decl_ref`)和 `scripts/lumos:57364`(`_lens_trusted_ref`)。
  - 讀取層 `_arch_targets_at`(`scripts/lumos:57397`)由代碼審派工鏡頭、推送前分級、code-loop check 和設計審共用。畢業只在分級與派工鏡頭兩處呼叫,新函式放在讀取層與比對層之間。
  - `scripts/lumos:57642` 的 check 已經同時讀起點版和頂端版宣告。S6 要改的說明正好接在這一處,沒有跨層直呼。
- 開關資料檔放 `scripts/templates/` 並登記進 `_VENDORED_TREE_FILES`,做法一致。
  - 對照 `scripts/lumos:31963` 到 `31986` 的清單,以及 `scripts/lumos:49083` 的 `_NOTE_REREAD_TEMPLATE`、`scripts/lumos:48000` 的 `_NOTE_AUDIT_TEMPLATE`。這兩個都是由 lumos 自己讀的範本。
  - 計劃已寫明要登記,且有逐檔比對的測試把關。
- 待補:設計沒說產生器怎麼寫節點、怎麼寫設定檔,見第 3 問。

## 2. 命名與錯誤處理:對齊

- `--write` 預設只印預覽、已存在就整批拒寫,有前例。
  - 對照 `scripts/lumos:69286`(`report-normalize --write`)和 `scripts/lumos:69386`(`--template` 搭 `--write`,已存在回 2、不動檔)。
  - 另一批命令用 `--apply`(`scripts/lumos:69529`),但前例已足以支持 `--write`,不列。
- 宣告形狀沿用既有 `{"path","node"}` 兩欄,沒有加欄位,讀法仍走 `_arch_targets_config`(`scripts/lumos:57307`)。
- 開關名與選項值是英文,說明文字是中文。這和 `review_roles` 的 `frontend|backend|none`(`scripts/lumos:37192`)一致。
- 不列 finding。

## 3. 第二種做法:不對齊 2 條

**(a) 規則來源在 Android 與 DDD、前端兩姊妹範本之間分成兩種。**
- 現行三份範本都是技能文件裡的「抄貼式」:`skills/lumos-project-notes/commands/target-arch-android-template.md`(226 行,以十二條 RULE 為主體)、`target-arch-ddd-template.md`(64 行)、`target-arch-frontend-template.md`(59 行)。步驟都是「開節點、貼 RULE、改日期、加宣告」。
- 這份計劃只讓 Android 變成「資料檔加產生器」,規則唯一來源搬到 `scripts/templates/`。DDD 和前端仍是技能文件內嵌。
- 後果有兩個:
  - 同一個專案要採用目標架構,有兩種流程可走,接手的人要猜。
  - Android 十二條裡的 DDD 六條,與 DDD 範本九條裡的七條 DDD 骨架,現在分放在兩處,各自維護。
- 計劃的 PRIOR-ART 與回退只談 Android,沒有說 DDD 與前端要不要一起搬,也沒有說為什麼只搬 Android。
- 要補的是:為什麼只有 Android 需要產生器,以及 DDD 規則在兩處之間誰是單源。
- 這是「另一份規則來源與既有範本並存」。

severity: major
blocking: 是
引句:「規則與 Konsist 測試的唯一來源搬到開關資料檔」
引句:「技能文件改成講開關與訪談題目,指向產生器;不再內嵌規則與測試全文。」
file: `skills/lumos-project-notes/commands/target-arch-ddd-template.md:8`
file: `skills/lumos-project-notes/commands/target-arch-frontend-template.md:1`

**(b) 設定檔寫入與節點寫入的做法沒講明,可能長出新的寫入路徑。**
- 現有程式裡沒有任何地方寫 `.lumos/config.json`。我 grep 過,所有出現處都是讀。所以「只加一鍵、其他鍵原樣保留」是專案裡第一次出現的設定檔寫入。
- 計劃寫的是「先寫暫存再整檔替換」,沒指到既有原語。專案已有 `_write_lf`(`scripts/lumos:28496`,暫存加 `os.replace`),新建檔前例是 `scripts/lumos:23332`。`atomic_write_verify`(`scripts/lumos:28530`)只用於改既有筆記開頭欄位,而且要持有筆記庫寫入鎖。
- 節點寫入同理。PRIOR-ART 寫「借 `lumos new` 寫節點的慣例」,但沒說是呼叫 `cmd_new`(`scripts/lumos:30766`)還是自己寫。`cmd_new` 做的檢查包括名稱、`--responsibility` 長度、`--code` 路徑和每支檔有家。節點摘要要帶十幾條 RULE,`cmd_new` 的空範本填不了,所以多半會自己寫,繞過那些檢查。
- 這裡我標 ⚠ 交編排者,不硬判成 major。理由是 `cmd_guard_plan` 已有不走 `cmd_new` 的先例,所以不一定是第二種做法。
- 要請計劃寫明三件事:節點與設定檔都走 `_write_lf`;節點寫入前先補上 `cmd_new` 的名稱與責任句檢查;寫完用 `lumos lint` 自驗。

severity: minor
blocking: 否
引句:「設定檔存在但沒有這一鍵時,只加這一鍵、其他鍵原樣保留」
引句:「先寫暫存再整檔替換」
file: `scripts/lumos:28496`

## 4. 落點:不合理

- 計劃的 `lands_in` 只列 `Systems/arch-alignment-lens`。
- 這一篇現在 98 行,掛 0 份計劃、2 行 KEY,沒寫負責範圍,管 `scripts/lumos` 和 `scripts/test_lumos.py`。
- 內容已經包含派席三問、對照組、張力、目標架構基準、DDD 範本、前端範本、Android 範本共七個章節。這份計劃再塞進去的是:
  - 六個開關的表;
  - 產生器子命令與它的寫入行為;
  - 舊檔 baseline 產生;
  - 一個新的資料檔。
- 其中產生器和資料檔不屬於「審查席怎麼挑對照」,是一個獨立的功能。畢業判定屬於可信版本與宣告讀法,留在該篇是合理的。
- 新資料檔 `scripts/templates/android-arch-target.md` 沒有 Systems 家。`lands_in` 沒指它,但鐵則 5 要求每支程式檔都有家。
- 建議的拆法:
  - 另開一篇 Systems 節點,例如 `arch-template-generator`,管產生器、開關和資料檔。
  - 畢業留在 `arch-alignment-lens`,在那篇加一小節並指路。

severity: minor
blocking: 否
引句:「Systems/arch-alignment-lens」
file: `docs/lumos-toolchain-knowledge/Systems/arch-alignment-lens.md:1`

不對齊共 3 條(含 1 條標 ⚠ 的待判),其中 major 1 條。
