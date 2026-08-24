# Self-audit: Systems/lumos-cli-write.md

角色:自足性審計員,不知道任何開發脈絡,只讀該筆記 + 對照 `scripts/lumos` 原始碼(不改任何檔案)。
問題:一個沒有背景的人照這篇描述去理解/使用 CLI 寫面,會不會被帶錯?
筆記路徑:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md`(稽核時 `updated: 2026-08-23`,`self_audit: sonnet/2026-08-21`)

---

## 逐條核對

### 開場與「七個原語」主表(body 69-84 行)

**站不住** —— 原語數量與清單本身都跟程式碼對不上。

- 第 69 行「(7 個子指令)」、第 73 行標題「七個原語」、表格只列 7 條:`set/append/self-audit/decision-add/decision-supersede/new/archive`。**完全漏了 `remove`。**
- 程式碼證據:`scripts/lumos:15602` `sub.add_parser("remove", ...)` 是正式註冊的第 8 個寫入子指令,`cmd_remove` 定義在 `scripts/lumos:7611`,且該函式**兩個分支都會走 `atomic_write_verify`**(list 分支 `scripts/lumos:7640`,純量分支 `scripts/lumos:7672`)——跟 set/append 一樣受寫後自驗保護,不是次等指令。
- 矛盾點:同一篇筆記的 summary KEY 行(第 23 行)自己說「**8個寫入原語**(set/append/remove/new/archive/decision-add/decision-supersede/self-audit)」——summary 是對的,但整個 body(標題、主表、"前五個才走 atomic_write_verify" 那句、已知限制、相關>實作落點、相關>回歸測試)全部漏掉 `remove`,前後不一致。
- 連帶錯誤:第 84 行「前五個(set/append/self-audit/decision-add/decision-supersede)才走 atomic_write_verify」——按程式碼應該是「前六個」(多算 remove),這句話會讓讀者以為 remove 沒有寫後自驗保護,或乾脆不知道有 remove 這條路可走,轉頭去手改 frontmatter(正是這篇開場白第 69 行自己警告要避免的行為)。
- 「相關」段(112-114 行)`實作落點`只列 `cmd_set/cmd_append/cmd_self_audit/cmd_decision_add/cmd_decision_supersede/cmd_new/cmd_archive`,漏 `cmd_remove`;`回歸測試`只列 `t_set_*/t_append_*/t_decision_*/t_archive_*/t_new_*`,漏 `t_remove_*`。實測 `scripts/test_lumos.py` 有 8 個 `t_remove_*` 測試(`t_remove_scalar_field:970`、`t_remove_basic:1262`、`t_remove_not_found_rc2_file_untouched:1272`、`t_remove_last_item_drops_key:1285`、`t_remove_exact_target_not_prefix:1296`、`t_remove_alias_and_path_forms_match:1307`、`t_remove_rejects_non_whitelist_key:1317`、`t_remove_core_refs_roundtrip:1326`),覆蓋不算薄,但這篇的「回歸測試」清單完全看不出來。

### `archive <days> [--apply]` 這一行(表格第 82 行)

**站不住** —— 指令語法寫錯,照抄會直接跑不動。

- 筆記寫的是 `archive <days> [--apply]`,把 `days`畫成位置參數(第一個必填引數)。
- 程式碼證據:`scripts/lumos:15648-15650`
  ```python
  p = sub.add_parser("archive", ...)
  p.add_argument("--days", type=int, default=180)
  p.add_argument("--apply", action="store_true", ...)
  ```
  `--days` 是**選填旗標**,預設 180,不是位置參數。照筆記字面打 `lumos archive 180 --apply` 會被 argparse 當成多餘的位置參數報錯;正確寫法是 `lumos archive --days 180 --apply`。

### `set <key>` 白名單(表格第 76 行)

**站不住(過期)** —— 數字跟程式碼現狀不符,且跟同篇 summary 自己打架。

- 第 76 行:「改 `SCALAR_KEYS`(以 scripts/lumos 常數為準,2026-08-21 為 9 鍵)」。
- 程式碼證據:`scripts/lumos:7278` 現在是 **10** 鍵:`status,updated,created,type,self_audit,signed_off,regen,pitfall_ask,pitfall_source,about_code_stamp`。
- 打臉來源就在同一篇:summary KEY 行(22 行,標日期 2026-08-23)明講「about_code_stamp 進 SCALAR_KEYS」。frontmatter `updated: 2026-08-23`,也就是這篇「已更新」到那一天,但 body 這行仍停在 2026-08-21 的舊數字沒有跟著改——單篇新舊打架的典型案例(CLAUDE.md 指名的那種,摘要裡有日期的 KEY 行比正文新)。
- 影響:不算誤導性太大(至少誠實標了日期讓人知道可能過期),但「以常數為準」的建議沒有被自己遵守。

### `append <key>` 清單(表格第 77 行)

**站不住** —— 用等號寫法暗示窮舉,實際只列一半。

- 第 77 行:「追加 `LIST_KEYS={verified_by,plan_refs,related,tags}`」,寫法像是把 LIST_KEYS 整個攤開。
- 程式碼證據:`scripts/lumos:7279` 現在是 **8** 鍵:`verified_by,plan_refs,related,tags,aliases,pitfall_when,core_refs,about_code`。少列了 `aliases/pitfall_when/core_refs/about_code` 四個。
- 對照 code 的實際拒絕訊息(`scripts/lumos:7598`):`append 只能加這些清單欄位:{sorted(LIST_KEYS)}` 會印出完整 8 項,跟筆記表格對不上——沒背景的人會被表格帶著以為只有 4 種清單欄位能 append,遇到 aliases/core_refs 要用 append 加值時會愣住(雖然實際執行會被 CLI 錯誤訊息糾正,但表格本身已經誤導)。
- 這行看起來是照抄 CLI `--help` 的簡短說明字串(`scripts/lumos:15593` 的 `help="list 欄位追加(verified_by/plan_refs/related/tags)"`)——help 文字本身就只是舉例,不是窮舉;筆記把它當成權威列表抄進主表是誤用來源。

### 「格式鐵則由原語結構性保證」段落引用 CLAUDE.md(95-100 行)

**站不住** —— 指錯文件,且暗示存在的「鐵則5」查無此物。

- 第 96 行:「鐵則完整清單(鐵則2/5等)在 `CLAUDE.md`;本節點只處理寫入相關鐵則(1/3/4)。」
- 查證:`CLAUDE.md` 裡唯一出現「鐵則」的地方是「### 三條鐵則」(整份 CLAUDE.md 內容我已核對,無「鐵則1」「鐵則5」等編號寫法),而且那節講的是完全不同主題(同次工作內寫回圖譜 / 用指令改欄位 / 收工前 lint+doctor / 承認風險要附回頭看條件)——跟 YAML 格式(wikilink list / 冒號引號 / 日期裸值)無關。
- 真正的「格式鐵則」編號 1-4 定義在 `skills/lumos-project-notes/reference.md:322-355`(標題正是「Frontmatter 鐵則」,兩個版本並存,都是 1-4 條:①多wikilink必YAML list ②block scalar內wikilink不索引 ③含「: 」長文要引號/block scalar ④同層禁重複鍵),`SKILL.md:44` 也只總結「四條」。**從頭到尾找不到「鐵則5」**——筆記寫「鐵則2/5等」等於暗示存在第 5 條,但源頭只有 4 條。
- 影響:沒背景的人照這句話的指示去 `CLAUDE.md` 找「鐵則2」「鐵則5」的完整說明,會找不到(那裡只有主題完全不同的「三條鐵則」),真正該去的地方是 skill 的 `reference.md`。這是會讓人在錯誤文件裡繞圈子的具體誤導。

### T1 寫後自驗 atomic 核心段(86-93 行,對應 summary KEY 20/24 行)

**站得住** —— 逐句對照 `atomic_write_verify` 程式碼(`scripts/lumos:7523-7546`),順序、失敗語意都正確:

1. `load_raw_for_edit` 確實拒 BOM(`scripts/lumos:7493`)、拒 CRLF(`scripts/lumos:7495`),報錯訊息會指路 `.gitattributes`/`dos2unix`——與筆記描述一致。
2. 驗證發生在**記憶體**裡的 `new_lines`/`new_fm_lines`(`parse_frontmatter(new_fm_lines)` 於 `scripts/lumos:7533`),`expected_check(fields)` 檢查(`scripts/lumos:7534`)與 lint 指紋比對(`scripts/lumos:7536-7538`)都在任何檔案寫入**之前**執行且用 `raise RuntimeError` 中止;`tmp = path.with_suffix(...)` 這行(`scripts/lumos:7540`)在兩個檢查關卡**之後**才出現,所以「檢查失敗時 tmp 根本未建立」的宣稱是對的。
3. 全過才 `_write_lf(tmp, text)` → `os.replace(tmp, path)`(`scripts/lumos:7542-7543`),`finally` 區塊確保殘留 tmp 被清掉。
4. 筆記特別標註「原文『先寫 tmp 再驗』順序寫反,2026-08-21 程式碼實證已訂正」——這個自我修正本身也跟現在的程式碼順序吻合,而且順帶點出 `atomic_write_verify` 函式自己的 docstring(`scripts/lumos:7524`「寫 tmp → re-parse 自驗」)其實才是舊的、跟真實執行順序不符的說法。這條算是筆記做對了「發現程式碼註解本身跟行為不一致」的細節工作。
5. `_write_lf` 唯一寫入原語、UTF-8/LF/no-BOM、用 `write_bytes` 不靠 `newline=`(3.10+ 限定)——對照 `scripts/lumos:7512-7520`,一致。

`decision-*` 走 `parse_decisions` 重解確認 valid/superseded_by 的宣稱,對照 `cmd_decision_supersede`(`scripts/lumos:7968-7975`)與 `cmd_decision_add`(`scripts/lumos:8029-8033`)的 `_check` 閉包,兩者都真的呼叫 `parse_decisions` 做 ID 精確驗證——站得住。

### `self-audit` 這行(78 行)

**站得住**。「內部即 set self_audit」對照 `cmd_self_audit`(`scripts/lumos:7578-7593`)最後一行 `return cmd_set(env, rel, "self_audit", f"{model}/{date}")`,逐字成立。`--model`/`--date` 旗標名稱、預設值(`sonnet`/今日)也跟 argparse 定義(`scripts/lumos:15608-15612`)一致。

### `decision-add` / `decision-supersede` 這兩行(79-80 行)

**站得住**。指令簽名(`<node> "<content>" --decided DATE [--context][--why]`、`<node> "<content子字串>" --by "..." [--ended DATE]`)對照 argparse(`scripts/lumos:15619-15623`、`15638-15643`)完全吻合,包含 `--by`/`--decided` 為必填、`--context`/`--why`/`--ended` 選填。已知限制段(106-107 行)講的「2-space 縮排,0-indent/tab 報錯」「已 superseded 拒絕重插」也都對照到 `cmd_decision_supersede` 裡的 Bug2/Bug3 檢查(`scripts/lumos:7906-7907`、`7939-7942`)成立。唯一小缺:表格沒提到 `#dN` 精確定址這個實際存在的用法(`scripts/lumos:15621` help 文字有寫),但這是「少講」不是「講錯」,不算誤導。

### `new` 這行(81 行)+ KEY 19 行

**站得住**。`TEMPLATES` 常數(`scripts/lumos:8424-8437`)剛好就是 `system/verification/issue/project` 四種,跟筆記完全一致。`new` 印「寫入當下教學」對照 `NEW_HINT` 常數與 `cmd_new` 尾段迴圈(`scripts/lumos:8513-8516`)屬實。KEY 19 行描述的 `--plan`/`--systems` 一鍵雙向、指到不存在節點就 rc2 且不建檔,對照 `cmd_new` 第 8482-8485 行(先檢查存在性、失敗就印錯誤並 `return 2`,此時 `path.mkdir`/`_write_lf` 都還沒執行)成立。

### `[test:]` 標記與測試存在性

**站得住**。逐一在 `scripts/test_lumos.py` grep 確認,以下全部是真實存在的測試函式,且抽查內容與宣稱相符:

- `t_lint_tag_value_enums`(13743)、`t_lint_aliases_declared`(13996)、`t_lint_decisions_nested_list_not_false_positive`(13954)——KEY 16-18 行引用,存在。
- `t_new_verification_bidirectional`(14108)——KEY 19 行引用,存在。
- `t_set_minimal_diff`(1193)、`t_append_exact_dedup`(1116)——KEY 24 行引用,存在。
- `t_append_block_key_rejected`(2201)——KEY 25 行引用,存在,且**內容真的測「summary(非白名單 key)用 append 應該 rc=2」**,跟該行「白名單外 key 直接 rc2」的宣稱一致(抽查了函式內容,非只驗名稱)。
- `t_set_status_syncs_tag`(1204)、`t_status_tag_drift_guard`(1230)——summary 尾行 TEST: 引用,存在。

沒有發現掛羊頭賣狗肉的測試名。這部分的自驗宣稱可信。

### 機器層 vs 專案層分工(102-103 行)

**站得住**。`cmd_install`(8666)、`cmd_uninstall`(8705)、`cmd_deinit`(8827)、`cmd_update`(9371)、`cmd_bootstrap`(9643)、`cmd_init`(9737)全部存在且對應筆記講的用途分類。

### decisions[] 三條(frontmatter 內建的 d1/d2/d3)

未逐條對照到單一行程式碼(這是設計決策的敘述,非可機械驗證的行為宣稱),但與本次讀到的 `atomic_write_verify`/`cmd_set`/`cmd_append`/decision-* 的實際分工一致,沒有發現內容上的矛盾。

---

## 總結

**這篇整體站不住(否)。**

不是內容全錯——T1 寫後自驗核心段、`[test:]` 測試引用、`self-audit`/`decision-add`/`decision-supersede`/`new` 的指令簽名都對照程式碼站得住,而且筆記自己抓出並訂正了一個程式碼 docstring 的順序錯誤(atomic_write_verify 的 tmp 寫入時序),這部分做得紮實。

但主體結構有一個系統性缺口 + 三個具體錯誤,會實際把沒背景的人帶偏:

1. **`remove` 從主表、已知限制、實作落點、回歸測試四處全部消失**,只活在 summary 的一行 KEY 裡。沒背景的人照著「七個原語」主表走,會完全不知道有這條指令可以清死背書 verified_by、拔掉降格後殘留的 core_refs、或刪掉 about_code_stamp——這正好是這篇開場白警告「別手改 frontmatter」想避免的下場。
2. **`archive <days> [--apply]` 語法寫錯**:`--days` 是選填旗標(預設 180),不是位置參數;照抄會被 argparse 拒絕。
3. **鐵則出處指錯文件**:引用「鐵則2/5 在 CLAUDE.md」,但 CLAUDE.md 的「三條鐵則」講的是完全不同主題,而且源頭(`skills/lumos-project-notes/reference.md`)只有 4 條規則,沒有「鐵則5」。照著找會撲空。
4. **SCALAR_KEYS/LIST_KEYS 的數字或清單過期**:body 表格停在「9 鍵」和 4 項清單,現狀是 10 鍵、8 項清單,且跟同篇 summary(標了新日期)自相矛盾。

## 修正建議

1. 在「七個原語」表格補回 `remove` 那一列,標題與開場白數字改成「8 個子指令/原語」;同步修「前五個(...)才走 atomic_write_verify」為含 remove 的六個。
2. 「已知限制」「相關>實作落點」「相關>回歸測試」三處補上 `remove`/`cmd_remove`/`t_remove_*`。
3. `archive` 那一行改成 `archive [--days N] [--apply]`,或至少加註「--days 選填,預設 180,非位置參數」。
4. 「鐵則完整清單」的指路改成 `skills/lumos-project-notes/reference.md`(或 `SKILL.md`「四條血換的開頭欄位鐵則」),不要指 `CLAUDE.md`;同時把「鐵則2/5」改成準確的「鐵則2/4」或講清楚源頭只有 4 條。
5. `set`/`append` 兩行的鍵值清單改成「以常數為準,目前 N 鍵/項(見 scripts/lumos:7278/7279)」這種指到常數而非手抄快照的寫法,或至少把日期和數字更新到跟 frontmatter `updated` 一致,避免下次改動常數又立刻過期。
