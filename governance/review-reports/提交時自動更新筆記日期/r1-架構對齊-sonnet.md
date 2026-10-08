severity: major

## 問 1 分層與依賴方向
掛鉤只呼叫 lumos、判定全在 lumos 裡,這個方向對齊:`scripts/hooks/pre-commit:208-222`(Gate H、Gate NS 都是 `"$CC_PY" lumos ... --staged --repo "$REPO_ROOT" || rc=$?`)。材料的 Gate UB 沿用同一寫法,分層沒問題。但這是第一道「會改檔」的掛鉤閘:既有三道都只讀;`scripts/hooks/` 裡唯一的 `git add` 只是 `scripts/hooks/pre-push:268` 的提示文字,不是前例。材料的 PRIOR-ART 只舉外部的 lint-staged,沒指出本專案沒有這種前例(見 F3)。
引句:「提交前掛鉤新增一道「Gate UB」(Gate PY 之後、Gate L 之前):照 home check 的回傳碼規矩」

## 問 2 命名與錯誤處理
指令名 `updated-bump --staged [--repo]` 與 `note-shape --staged --repo`(`scripts/lumos:30753`)、`home check --staged`(`scripts/lumos:28373`)同形;環境變數 `LUMOS_SKIP_UPDATED_BUMP=1` 只認 1,跟 `LUMOS_SKIP_NOTE_SHAPE` 一致(`scripts/lumos:30772`);rc1 擋、其餘放行跟 Gate H/NS 一致(`scripts/hooks/pre-commit:219-221`、`232-234`)。落差只有一處:既有跳過會寫治理帳(見 F3)。
引句:「`LUMOS_SKIP_UPDATED_BUMP=1`(只認 1)」

## 問 3 第二種做法
有兩處另起一套(F1 寫檔、F2 讀暫存與判跳過)。讀內容那段(`_nodehome_reader`、`_nodehome_cat_blobs`)是沿用既有的,對齊。
引句:「改 `updated` 那一行自寫一支只換那一行的小函式」

## 問 4 落點
`lands_in` 只寫 Systems/lumos-cli-write,但本案同時改 `scripts/hooks/pre-commit`;那支檔的家是 `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md` 與 `每支檔有家.md`(about_code 有列,`筆記內容閘.md:8-12`),而 `Systems/lumos-cli-write.md:85-86` 的 about_code 只有 `scripts/lumos`。依專案鐵則 5,掛鉤那段的說明要寫進掛鉤的家(筆記內容閘),CLI 指令本體寫進 lumos-cli-write;兩邊都要列進 lands_in。
引句:「寫回 [[Systems/lumos-cli-write]];兩份 skill 速查照範圍第 5 條。」

## F1 寫 updated 另寫一套,沒走既有寫入路徑
severity: major
blocking: 是
引句:「改 `updated` 那一行自寫一支只換那一行的小函式」
既有寫 `updated` 的唯一做法:`cmd_set` 在 `_vault_write_lock` 下(`scripts/lumos:18019-18021`),`load_raw_for_edit`(`scripts/lumos:17842`,拒 BOM/CRLF)讀、`edit_fm_scalar`(`scripts/lumos:17648`)改欄位、`atomic_write_verify`(`scripts/lumos:17893`)原子寫並回讀驗證;`updated` 本來就在 `SCALAR_KEYS`(`Systems/lumos-cli-write.md:39`)。材料自寫換行函式,等於第二套寫檔:沒有鎖、沒有 BOM/CRLF 拒絕、沒有原子寫與回讀驗證。這道又是在提交途中改使用者的檔,風險比 set 更高。應抽出共用的「改某篇的純量欄位」函式(或直接叫 set 的內層),不另寫。

## F2 讀暫存清單與判跳過的寫法另起一套
severity: minor
⚠
blocking: 否
引句:「`git diff --cached --name-only --no-renames --diff-filter=AM -z` 取暫存清單」
既有同類閘用 `_nodehome_list(root, "index")` 加 `_nodehome_changes(root, head, "index")` 取暫存內容與改動(`scripts/lumos:28385-28390`、`30781-30795`)。材料同一份文件的 PRIOR-ART 說沿用 `_nodehome_list`,做法第 1 步卻直接呼叫 git diff,兩處說法不一致;直呼也繞過 NFC 正規化與衝突階段排除(`scripts/lumos:27381-27399`)。另外判「進行中」只有 MERGE_HEAD 有前例(`scripts/lumos:28385`、`29758`、`30781`),材料新增 CHERRY_PICK_HEAD、REVERT_HEAD、rebase、SQUASH_MSG、GIT_INDEX_FILE 一組,repo 內沒有現成共用判法,建議抽一支共用函式,別在新指令內自刻一份。判不準這算「第二種判合併」還是「合理擴充」,故 minor ⚠。

## F3 跳過沒有進治理帳
severity: minor
blocking: 否
引句:「`GIT_INDEX_FILE` 指的不是預設索引」
既有閘跳過(環境變數、合併、淺層)都經 `_gate_event_or_warn` 記帳(`scripts/lumos:30773-30778`),或至少印一句說明;材料只印一句、沒寫記不記帳,跟 `LUMOS_SKIP_NOTE_SHAPE` 那條「跳過留帳」的規矩不同。同時,本案是首道會改檔的掛鉤、本專案無前例(問 1),材料沒說明為何不怕「掛鉤裡 `git add`」與別的並行會談共用索引互相踩(鐵則裡提過同工作目錄有別的會談)。
