severity: minor

**spec-freeze 清理與原子寫入**:已讀,無 finding。
- 暫存 index 目錄放在 `finally` 的 `rmtree` 裡。Ctrl-C 或任何一步失敗都會刪。
- `--out` 用「暫存檔名每次不同、O_EXCL 建立、`os.replace`」寫入。
- 我實測了一次完整跑法:跑完沒有留下 `/tmp/lumos-spec-freeze-*`。
- 我沒有實測兩次 spec-freeze 同時跑。依程式推演,同一份計劃會是兩邊都建提交,最後一個 `os.replace` 贏,內容相同。
- 計劃在兩次呼叫之間被改動時,先檢查通過的那邊印出的提交編號會和 `--out` 內容對不上。在單人、依序操作的威脅模型下不構成問題,所以不列 finding。

severity: minor
blocking: 否 — 超出預算時只是掛鉤逾時、少附鏡頭並多一行逾時說明,派工不會被擋,也不會寫壞資料。
引句:「elif commit and cand not in tried and len(only) < _LENS_SPEC_MAX_FILES:」
問題:提交寫法的計劃有三處會依計劃內容跑一個 git 子行程,數量沒有上限,也不受 `_LENS_SPEC_BUDGET`(30 秒)管。
- `_lens_spec_code_files`:上限條件是 `len(only) < 5`,只有「提交裡有」的才會推進。「提交裡也沒有」的候選永遠不會讓 `only` 增加,所以每個不同的 `scripts/...` 字串都要跑一次 `ls-tree`。
- `_lens_spec_linked`:每個不同的 `[[Systems/x]]` 連結,如果會談目錄沒有,就跑一次 `_spec_commit_has`(`cat-file -e`)。
- `_nodehome_landing_sizes`:每個 `lands_in` 項目也是同樣的呼叫。
- 這三處都在 `impact` 迴圈的預算檢查之前執行,而且新增的 `_LENS_SPEC_CODE_BT_RE` 讓反引號路徑也被算進候選。

具體失敗情境:
- 大計劃的反引號程式路徑和 `[[Systems/…]]` 連結各約 500 個不同的值(檔案約 25KB),都不在會談目錄,也不在凍結提交裡。
- 我實測這個計劃:`dispatch-lens --spec <提交>:<路徑> --json` 跑了 28.2 秒(約 1000 次 git 呼叫,macOS 上每次約 28ms)。
- 6000 組(273KB)的計劃,我等了 130 秒還沒跑完,就停掉了。
- 計劃上限是 1MB,掛鉤內層預算是 `_lens_timeout()`(約 45 秒)。所以數百個連結的計劃就會讓掛鉤逾時,設計審的派工詞只剩逾時說明,沒有固定席。工作樹寫法沒有這些 git 呼叫,不受影響。
- 修法:
  - 把這幾處的 git 呼叫收進同一個 deadline。
  - 或者改成一次 `ls-tree -r` / `cat-file --batch-check` 批次查。
  - 或者替「提交裡也沒有」的候選也設數量上限。

佐證:
- file: `scripts/lumos`,位置在 patch 的 `_lens_spec_code_files`、`_lens_spec_linked`、`_nodehome_landing_sizes` 三個函式。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/hooks/claude/dispatch-lens-hook.py:100`(`_lens_timeout`)

severity: minor
blocking: 否 — 只會在 `--out` 旁留下一個小暫存檔,沒有污染 repo,也沒有污染快照內容。
引句:「except OSError:」
問題:`_spec_freeze_write` 的暫存檔只在 `OSError` 時清理。
- 在 `os.open` 建立暫存檔之後、`os.replace` 之前收到 Ctrl-C(`KeyboardInterrupt`)或 SIGTERM,檔案就留在 `--out` 旁邊,檔名是 `<out>.<pid>-<8 位十六進位>.tmp-spec-freeze`。
- 之後重跑不會清掉它,因為檔名每次都不同。
- 實務上這個視窗只有寫入幾 KB 的瞬間,我只讀程式推演,沒有實測。

佐證:file: `scripts/lumos`(patch 的 `_spec_freeze_write`)

**掛鉤裡新增的 git 呼叫對預算的影響**:除了上面第一條,已讀,無 finding。每次 git 呼叫仍帶 `timeout=20`,但沒有被內層預算夾住;這一點併入第一條。

**表態記錄反駁**:`py-hotpath na`(沒有大量資料的熱迴圈)與 `py-memory na` 的說法不成立。計劃連結或程式路徑一多,迴圈內就是一路跑 git 子行程。

最高等級 minor,blocking 0 條。
