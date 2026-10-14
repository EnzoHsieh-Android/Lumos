severity: minor

這一輪我沒找到會弄壞既有功能的 bug,只有一條會在慢機器上偶發誤擋的小問題。

我在 `reread-fp` 工作樹跑了這些測試子集,全綠:
- `-k reread`:335 個
- `-k codeloop_default_base`:9 個
- `-k push_range`:22 個
- `-k delguard`:100 個
- `-k security_seat`:67 個
- `-k note_shape`:279 個

我沒有做慢機器或逾時的模擬,下面這條的失敗情境是讀程式推出來的。

severity: minor
blocking: 否 — 只在逾時或慢機器下偶發,而且是誤擋,不是漏判。
引句:「dl = None if deadline is None else deadline - _NOTE_REREAD_FP_RESERVE」
問題:v2 對照指紋算不算得出來,取決於有沒有截止時間。`reread-prepare` 呼叫 `_note_reread_fp_info(scan, rel)` 不傳 deadline,所以 `dl` 是 None,v2 永遠算得出來。推送前的 `reread-check` 傳的是 30 秒預算減 3 秒保留。`_note_reread_fp_base` 和 `_note_reread_fp_file` 逾時或剩不到時間時,回傳「逾時」並退回 v1。
具體失敗情境:
1. 在大 repo 或慢磁碟上,prepare 用 v2 產出名為 v2 指紋的紀錄並提交。
2. 推送前 check 在同一版 refs 下,因為 scan 已用掉大半預算,v2 退回 v1。
3. v1 指紋對不上 v2 命名的紀錄(主線改過 about_code 的檔之後 v1 就會變),所以 `_note_reread_hits` 判成「沒對照」。
4. block 模式下推送被擋,人重跑 prepare 又得到 v2,看起來像沒解的迴圈。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos:36200`(`_note_reread_fp_base`)與 `scripts/lumos:36644`(`_note_reread_item`)``

已讀,無 finding 的部分:
- **手動 code-loop 預設起點搬家**:`_codeloop_default_base` 變成 `_lens_default_base(repo_root)` 的薄包裝,語意跟原本逐行對得上。對得上的點:
  - 遠端取得方式相同。
  - 本機 main/master 照舊加入候選。
  - 都是 `merge-base --all HEAD`。
  - 都用 `_push_pick_base` 取歷史最長。
  - `deadline=None` 時 `_lens_git_dl` 和 `_lens_git` 完全相同。
  - 該函式的測試 9 個全綠。
- **`_patch_file_changes` 的資安席呼叫者**:兩個新參數預設值是 `headers=True, lf_only=False`,走回舊分支,所以資安席的指紋位元不變。`"@@" + x if headers else "@@"` 的優先序也對。
- **回頭重讀第二層表態**:`_note_reread_layer2` 依筆記路徑讀紀錄,不看對照指紋,所以 v2 命名的紀錄不影響它。
- **`_note_reread_prepare_todo`**:從 `done` 集合改成 `hits` dict 後,邏輯和舊的等價(wip 扣除條件改成 `not hits.get(rel) and fps in wip`)。
- **治理帳事件的讀者**:
  - 新增的 `branch` 欄只出現在 `note-reread` 事件。
  - 讀 `branch` 的程式(`_codeloop_ledger_events`、`_codeloop_read_from_ledger`、表態讀取)都先篩 `gate == "code-loop"`,不會讀到它。
  - `layer1_fps` 只是多了 `ver` 鍵,沒拿掉舊鍵。
  - `covered`、`none` 這兩種原本沒有 extra 的帳加上 extra 後,`_gate_event_fit` 會先丟 `v2_only`,不會超過 4096 位元組。
- **v1 路徑的 diff 參數**:`_note_reread_diff` 在 v1 路徑加了 `core.precomposeunicode=false`。傳入的路徑本來就是 `scan["changed"]` 裡 git 的原樣路徑,所以行為一致,既有 reread 測試也沒紅。

最高等級是 minor,blocking 共 0 條。
