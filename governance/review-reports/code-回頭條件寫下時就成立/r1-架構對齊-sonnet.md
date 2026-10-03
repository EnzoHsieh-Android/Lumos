severity: minor

# 架構對齊審查(code-born-r1)

## Z1 淺層 clone 判法又寫了第三份行內版本,而專案已有 helper
severity: minor
blocking: 否
引句:「sh = _lens_git(root, "rev-parse", "--is-shallow-repository")」
file: `scripts/lumos:5549`(`_git_is_shallow` 既有 helper)、`scripts/lumos:29504`、`scripts/lumos:30160`(兩處行內版本)
說明:鄰居本身就不一致(一支 helper、兩處行內 `_lens_git` + `stdout.strip() == "true"`)。新碼照行內那兩處寫,結構上沒有引入新做法,只是讓行內版本變成三份;`_lens_git` 回 None(git 跑不起來)時三處都當成「不是淺層」,新碼也一樣。

## Z2 `_DriftBornHistory._text` 用 None / False 兩個哨兵值,不是鄰居的「回 None=判不了」
severity: minor
blocking: 否
引句:「第 i 版的文字;那一版沒有這篇回 None;讀不了回 False(原因在 self.err)。」
file: `scripts/lumos:29893`(`_note_history_states` 的 None=讀不到)、`scripts/lumos:26543`(`_nodehome_cat_blobs` 的 None=那版沒有或判不了)
說明:鄰居慣例是失敗一律回 None、原因另外帶(tuple 或訊息)。這裡 None 與 False 意思相反,呼叫端靠 `is False` 區分,容易被改成 `if not tx` 而弄反。同類型的 `birth` 回 (值, 原因) 二元組,與鄰居 `_drift_row_unread` / 回 (None, why) 是一致的,只有 `_text` 例外。

## Z3 判不了原因用字串字面值在 annotate 裡比對
severity: minor
blocking: 否
引句:「if why in ("不在第一版", "歷史查不到這篇") and where == "disk":」
file: `scripts/lumos:32873`(`_drift_probe_scan` 的原因字串只當輸出、不拿來分支)
說明:鄰居把原因當最終輸出文字;這裡 `birth` 吐出的原因被 `_drift_born_annotate` 再依字面值改寫,兩支函式靠中文字串耦合。結構對,但改字會悄悄失效。

## Z4 `_DRIFT_BORN_MAX_COMMITS = 6` 與 `_DRIFT_LS_CACHE` 上限 8 只靠註解連動
severity: minor
blocking: 否
引句:「_DRIFT_BORN_MAX_COMMITS = 6    # 一次 scan 最多在幾個不同的提交判條件(列樹快取上限 8,留兩格給終點;每個約 2 秒)」
file: `scripts/lumos:32250`(`_drift_list` 內的 `if len(_DRIFT_LS_CACHE) >= 8:` 寫死數字)
說明:鄰居的 8 是 `_drift_list` 內寫死的字面值,沒有模組常數可引用,新常數只能靠註解對應;之後有人改 8,6 不會跟著變、清全部快取會讓終點的樹被擠掉。非新做法,是缺連動。

## Z5 ⚠ partial clone 判法(`extensions.partialClone`)專案裡沒有既有做法可對
severity: minor
blocking: 否
引句:「pc = _lens_git(root, "config", "--get", "extensions.partialClone")」
file: `scripts/lumos:32917`(grep `partialClone|promisor` 全檔只有這一處)
說明:交編排者。沒有鄰居可比,不硬判。附註:只看 `extensions.partialClone`,不看各 remote 的 `promisor` 設定,但專案沒有對照可說不一致。

## 三問

1. 分層與依賴方向:對齊。新碼放在 `_drift_probe_scan` 之後、「表態」段之前,與 `_drift_probe_*` 同區;呼叫 `_note_versions`(從 `_note_status_seq` 抽出,`scripts/lumos:29860`)、`_drift_tree_env`、`_drift_probe_tree`、`_drift_vault_rel`、`_drift_probe_prefetch`、`_drift_probe_line`、`_nodehome_cat_blobs`,都是 `cmd_drift_scan`(`scripts/lumos:35293`)已用的同一套;`cmd_drift_scan` 呼叫 annotate,`_drift_scan_print` 只讀 `born`,方向與鄰居一致,沒有跨層直呼。`_drift_born_tree` 重複 `cmd_drift_scan` 的「vault_rel + tree_env」兩行,量小不算第二種做法。
2. 命名與錯誤處理:大致對齊。`_drift_born_*` 前綴、`_over()` 用 `>=`(同 `scripts/lumos:32880`、`:32378`)、判不了不印例外、不寫治理帳、中文原因訊息、deadline 傳法都與鄰居同。偏離只有 Z2(None/False 哨兵)、Z3(字串耦合)兩個 minor。
3. 第二種做法:
   - `_DriftBornHistory`:`_note_history_states`(`scripts/lumos:29893`)與 `_note_base_status` 是「一次讀全部」,這裡是分 32 版讀、碰到邊界就停;但版本清單共用 `_note_versions`、批次讀共用 `_nodehome_cat_blobs`,只有「分段+停點」是新的,而它的需求(不讀完整歷史)是計劃寫明的,且鄰居(`_DriftProbeTree`,`scripts/lumos:32364`)也是用 class 帶快取與 deadline 的先例。判不算第二套歷史走訪。
   - `_git_log_sha_status_paths`:取代並刪除了 `_git_log_sha_paths`(diff 內已移除、全檔 grep 無殘留呼叫),不是並存;`--name-status -z` 其餘解析器(`scripts/lumos:26439` 的 diff-tree 版)輸入形狀不同(沒有 sha 前綴),不算重複。
   - `_drift_born_env_err`:淺層判法是第三份行內版本(Z1),partial clone 無先例(Z5);不構成新的 git 呼叫包裝,仍走 `_lens_git`。

不對齊共 5 條,其中 major 0 條
