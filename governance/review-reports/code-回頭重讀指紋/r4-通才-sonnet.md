severity: minor

我讀完修補差異,沒發現會弄壞既有功能的問題,只有兩條 minor。在隔離副本(程式放進暫存目錄,原目錄未動)跑了 `-k reread_fp` 子集,149 過、0 紅。實驗暫存目錄還沒刪,下面會處理。

## Finding

severity: minor
blocking: 否 — 只在 fork 工作流(origin 是 fork、本機 main 追蹤正本)直接推 main 時誤擋;可用 LUMOS_SKIP_REREAD_CHECK=1 單次跳過,且 block 模式加 `--gate` 才擋。
引句:「分岔點必須是它的祖先(或相等),不是就丟 _NoteRereadStop」
問題:`_note_reread_bp_vs_remote` 假設分岔點一定是「被推那條遠端 ref」的祖先。但分岔點是對全部主線候選一起算 `merge-base --all` 再取歷史最長的(`_lens_default_base`)。候選包含 `main@{upstream}`,fork 工作流裡它會指到正本 `upstream/main`。
具體失敗情境:
- origin 是 fork,本機 main 追蹤 `upstream/main`。
- 使用者把 `upstream/main` 合進本機 main 再加自己的提交,然後 `git push origin main`。
- 這時分岔點落在 `upstream/main` 頂端,比 fork 的 origin/main(pre-push 給的舊值)新,所以不是舊值的祖先。
- 結果:丟 `_NoteRereadStop`,訊息叫人 `git fetch origin`,但 fetch 修不好,只能跳過。
- 這個誤擋只在「被推的 ref 剛好是候選之一」時出現,所以限定在推主線。
- 我沒有實際造出 fork 場景跑,這條是從程式推得的。
佐證:`scripts/lumos:37640-37671`(`_note_reread_bp_vs_remote`)、`scripts/lumos:48102`(`_push_mainlines` 候選含 `main@{upstream}`)。

severity: minor
blocking: 否 — 有現成的單次跳過,warn 模式不受影響;只是擋下結果會隨機器負載不同。
引句:「代價是改動極大、指紋這一步在 _NOTE_REREAD_BUDGET_SEC 內算不完的分支」
問題:逾時改成照擋之後,「逾時沒算出新版指紋」是看當下機器負載的非確定結果。分支大小在邊緣、機器忙(多個 Claude 會談同時跑)時,同一份已記好新版紀錄的分支,這次逾時就退回 v1 而擋下,下次沒逾時就過。清單文字和註解卻寫「重跑也一樣」。這句只對真的大到每次都逾時的分支成立;邊緣情況重跑會過,使用者可能不必要地用跳過變數,每次跳過都留帳。
具體失敗情境:
- 分支剛好讓指紋這一步用掉約 25 到 27 秒。
- 第一次推送在負載高時逾時而擋下。
- 同一份工作再推一次就過。
佐證:`scripts/lumos:37739-37743`(`_note_reread_blocking` 說明)、`scripts/lumos:37836-37840`(清單那句)。

## 已讀,無 finding

- **入口強制 `GIT_NO_REPLACE_OBJECTS=1`**:
  - 它設在 `main()` 開頭,所有子行程繼承。專案內沒有任何子命令靠 `git replace`(grep `scripts/lumos` 的 `refs/replace`、`git replace` 都是 0)。
  - 我把那一行拿掉跑 `t_reread_fp_ignores_replace_refs`,測試會紅,所以它抓得到這個還原。
  - 我順手發現測試行程裡 `_lumos_parser_tree()` 會在行程內呼叫 `main()`,這個環境變數會漏進測試行程。實測確認會漏,但只有這一支測試用 `git replace`,實際影響可忽略。
- **`_note_reread_fp_walk_keys` 抽出**:算法與舊的 `sorted({_nodehome_key(v) …})` 逐字相同,指紋輸入的鍵與順序沒變。預讀順序改成照候選、每篇照同一組鍵走,和算指紋實際順序一致;去重後順序仍穩定。
- **縮排鏈跳過標點行**:
  - 這會改變 v2 的標籤。但 `e0da694b` 上沒有 v2(「指紋算法 v2」與 `_note_reread_hunk_nodes` 出現次數都是 0),所以沒有舊的 v2 紀錄會失效。
  - 內聯迴圈和 `_note_reread_indent` 一致,有專屬測試 `t_reread_fp_indent_inline_same` 綁住,我跑的子集包含它。
  - 錨點行永遠不是被跳過的行,「全是跳過行」的無限深起點分支也在 `continue` 之前處理,沒有漏。
- **v1 舊紀錄**:v1 對照指紋的算法沒動,逾時退回 v1 的路徑行為如前,只差現在會擋。
- **`hunk_nodes` 逾時**:`_note_reread_hunk_chains` 用 `or ()` 處理 None。`_note_reread_fp_tags` 在 `want` 為空、`data=None` 時回 `[]`,不會被誤判成逾時。prepare 沒有截止時間時 `_note_reread_fp_expired(None)` 回 False,行為不變。
- **warn 模式與 rc**:`_note_reread_blocking` 開頭有 `not hard` 就回 False,warn 模式下逾時的篇只提醒、rc 0。`_note_reread_stop` 在 warn 模式下是 undecidable,rc 0,這與其他判不了的路徑一致。
- **推主線祖先核對對既有流程**:
  - 新分支首推(舊值全 0)、舊值本機找不到(force push 蓋掉)、非主線分支,都在 `return` 前離開,不受影響。
  - 一般推主線時,分岔點是本機追蹤 ref 的祖先,而本機追蹤 ref 不會超前遠端現值,所以放行;對照測試 `t_reread_fp_forged_tracking_ref_blocks` ②③ 也覆蓋了。
  - 主線候選查詢失敗時,即使不是推主線也會降成 v1(`why="git 失敗"`)。這只在 git 本身壞掉時發生,屬保守方向,我沒當 finding。

## 收尾

我做了一次暫存清理,但實驗副本(含連到真 repo 的符號連結)沒刪完:
- 實驗目錄:`/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-Backend-improve/fe5c4f58-e7fb-477f-be55-0823b5438608/scratchpad/cr-rf4-通才/`
- 測試紅時留下的 `gctl-run-*` 現場:`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 下三份,是 `gctl-run-49o11_g7`、`gctl-run-5jczul6q`、`gctl-run-47eizs6_`

這些都是我造的,我現在去刪。

最高等級 minor,blocking 0 條。
