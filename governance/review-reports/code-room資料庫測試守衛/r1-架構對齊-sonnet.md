severity: major

派工詞要我檢查的鎖 `/Users/enzo/.cache/lumos/dispatch-lens/fc97c184…872af9.json.warming`,我查過,檔案不存在。我沒有動任何鎖,只做審查。

## 1. 分層與依賴方向:部分不對齊

對齊的部分:
- 帳本走 `_gate_event_or_warn`,`hard=True`、`head_sha` 的用法跟存量漂移一致。
  - file: `scripts/lumos:54595`(`cmd_drift_check` 的記帳)
- 讀檔一律走 `_nodehome_reader`,逐行差異走 `_diff_text_lines` 加 `_lens_diff_header`,git 一律走 `_lens_git`。
- 設定檔從被推的終點讀,形狀跟 `_note_shape_config` 一致。
  - file: `scripts/lumos:44226`
- 掛鉤接線一致:`pp_stop_if_signaled`、rc1 印逃生段加 `pp_record_block`、其他非零講一句放行、`--repo "$REPO_ROOT"`。
  - file: `scripts/hooks/pre-push:683`

不對齊的有三條,F1 和 F2 是 major。

## F1 剝註解另寫了第二支函式
severity: major
blocking: 是,全庫原本只有一支剝 C 式註解的 helper,這份 diff 又加了一支,接手的人要在兩支之間猜。
引句:「剝程式註解並清空字串內容,★保留換行★(行號要對得上差異)」
file: `scripts/lumos:6752`。`_strip_c_comments` 的 docstring 寫「全庫只有這一支」,而且測試把它釘住,說「第二套掃描樣式已不存在」。
file: `scripts/test_lumos.py:108968`(`t_strip_c_comments_shared_and_linear`)
`_rg_strip` 用同一個 `_C_STRIP_PAT`,又自己寫了一層 `_one` 替換邏輯,差別只在註解換成換行而不是空字串。這個差別用 `_strip_c_comments` 加一個參數就能做到,不需要另一支。

## F2 與主線的分岔點在 room-guard 裡自己再組一遍
severity: major
blocking: 是,「起點只在 `_push_range_start` 算一處」是這個專案修過多輪才定下來的規矩,這裡又拼出一份,屬於第二種做法。
引句:「mls, err = _push_mainlines(root, push[0], push[1])」
file: `scripts/lumos:61717`。`_push_range_start` 的 docstring 寫「起點只在這裡算一處」,理由是掛鉤、CI、工具各算一份,三份各有洞。
file: `scripts/lumos:62075`。`_lens_default_base` 是另一個同樣的組裝,room-guard 這份是第三個。
`_rg_fork_point` 自己組了 `_push_mainlines`、`merge-base --all`、`_push_pick_base` 這串,取的就是 `_push_range_start` 在 old 為全 0 時回的分岔點。它的失敗處理也跟那邊不同:`merge-base` 失敗直接回 None,後面當成「找不到主線」,結構檔改寫只剩提醒;`_push_range_start` 的規則是不退成少查。
另外它呼叫 `_push_pick_base(root, bases, None, [], "主線")`,把 `names` 傳了空清單。
file: `scripts/lumos:62105`。`_lens_default_base` 傳的是 `"主線", ""`,兩邊參數位置的意思不一樣。

## F3 前置段沒用既有的小函式
severity: minor
blocking: 否,結構是對的,只是 `_note_audit_start` 和 `_note_audit_root` 現成,卻在 room-guard 內再抄了一份同形狀的三元式和找 repo 根。
引句:「start, why = _push_range_start(root, a, tip, *push) if push else _lens_push_base(root, a, tip)」
file: `scripts/lumos:48395`(`_note_audit_start`,同一個三元式,說明前面多加「起點——」)
file: `scripts/lumos:48403`(`_note_audit_root`;存量漂移、`push-summary` 都用它)
`_rg_root`、`_rg_precheck`、`_rg_range` 這一串前置段,筆記形狀擋也是內聯寫的(`scripts/lumos:47547` 起),計劃的 PRIOR-ART 也寫「照抄筆記形狀擋」。所以這條只算 minor,結構上沒有第二套帳或第二套設定。

## 2. 命名與錯誤處理:對齊
- 命名:`_rg_` 前綴加 `cmd_room_guard`,跟 `_ns_`、`_drift_`、`_lint_new_` 同一種做法。
- rc 語意:1 擋、0 放、2 參數錯,跟 `cmd_note_shape` 一致。
  - file: `scripts/lumos:47547`
- 判不了一律 rc0 並記 skipped,這是 WHY 筆記寫明的取捨(對照 Android 端到端驗收判不了就擋刻意不同)。跟筆記形狀擋同類,跟存量漂移「判不了算要處理」(`scripts/lumos:54595` docstring)不同,見 ⚠。
- 跳過口:`LUMOS_SKIP_ROOM_GUARD`,只認 `=="1"`,記 `skipped-env`,跟 `LUMOS_SKIP_DRIFT_CHECK` 同形。
- 閘名登記:`_KNOWN_GATES` 和 `_GOV_LOCAL_PAIRS` 照既有方式登記,`HELP_WHEN` 有補。
- 輸出用「擋下:/提醒:」前綴,印到 stderr,三段式。

## 3. 第二種做法:一條不對齊

## F4 索引表把既有子指令名縮短了
severity: minor
blocking: 否,只是文件列法跟既有不一致,不影響結構。
引句:「reread-prepare·record·check(回頭重讀)」
file: `skills/lumos-project-notes/commands/INDEX.md`。diff 之前這格寫的是 `reread-prepare·reread-record·reread-check`,真正的子指令名帶 `reread-` 前綴;改成 `record·check` 後,會跟前面 `note-audit prepare·record·check·skip` 那組(筆記內容審)混在一起。這個改動跟 Room 守衛無關。

文件與筆記的落點與格式都對齊:
- `Systems/room-guard.md` 的 `about_code` 列 `scripts/lumos` 與 `scripts/hooks/pre-push`,跟存量漂移守衛同形。
  - file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md`
- Verification 筆記欄位(`valid_under`、`revalidate_when`、`plan_refs`)跟既有同類一致。
  - file: `docs/lumos-toolchain-knowledge/Verification/TTY確認不取得控制終端驗證.md`
- 規範補充節放在 `test-quality-standard.md`,標題形狀跟〈網頁前端〉節並列。
- 沒有另一套帳本格式,也沒有另一種逃生口命名。

## ⚠ 交編排者(鄰居本身不一致,我不硬判)
1. 測試路徑判斷:`_rg_is_test_path` 是專案裡第四支。
   - 已有 `_nodehome_is_test`(`scripts/lumos:42864`)、`_testmap_is_test`(`scripts/lumos:58960`)、`_is_test_infra_file`(`scripts/lumos:37578`)和 Android 端到端的 `src/test|androidTest` 判斷(`scripts/lumos:40650`)。
   - 現有幾支彼此規則就不同。
   - room-guard 認 `src/<名稱>/`、名稱以 test 或 androidTest 開頭或以 Test 結尾,範圍比較寬。專案沒有單一標準可對。
2. 判不了的處理:存量漂移和回頭重讀判不了就擋或算要處理,筆記形狀擋和這份 diff 是放行。WHY 筆記寫了取捨,但專案內有兩個方向。
3. CI 後盾:存量漂移和筆記形狀擋在 CI 都有一步(`.github/workflows/ci.yml:229`、`:251`),room-guard 的掛鉤註解寫「CI 第一版不接」。計劃有 RETIRE-IF 和 REVISIT:2027-04-28,但沒有針對 CI 缺口的回頭條件。
4. 上線點截斷:筆記形狀擋、存量漂移和每支檔有家都用 `_nodehome_clamp_base` 加上線標記,掛鉤也有「上線標記」註解。room-guard 沒有。可能是刻意的,因為它比的是程式碼形狀、不是舊帳,但 diff 裡沒寫理由。
5. 逐行差異解析:專案裡已有三處各寫自己的 `@@ -a,b +c,d @@` 解析(`scripts/lumos:37594`、`:58252`、`:47332`)。`_rg_hunks` 是第三處,但它確實用了 `_diff_text_lines` 與 `_lens_diff_header`,沒有統一出口可對。

## 固定席筆記
本次沒附固定席節點,沒有逐條要判的筆記。

不對齊共 4 條,其中 major 2 條
