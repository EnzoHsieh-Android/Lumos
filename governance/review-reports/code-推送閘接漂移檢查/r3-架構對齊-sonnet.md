severity: minor

# r3 架構對齊席(sonnet)

## F1 起點與主線判法變成兩套並存,理由與收斂路只寫在圖譜、程式碼裡沒有指回去
severity: minor
blocking: 否
引句:「def _push_range_start(repo_root, old, tip, remote, pushed_ref):」
佐證行:file: `scripts/lumos:33067`(既有 _lens_push_base,起點判法,home check、note-shape 與其他 note-audit 閘共用)
佐證行:file: `scripts/lumos:33214`(既有 _mainline_ref,主線判法;另有 24757、28952、34144、35006 等呼叫端與 _ns_mainline_refs 包裝)
1. 現況:同一件事「推送範圍的起點」現在有兩套。`_lens_push_base`(舊值找得到就直接用、全 0 或找不到才算分岔點,主線只認 main/master 的 upstream)與新的 `_push_range_start`(自己的 `_push_mainline` 候選序、`merge-base --all`、`_push_pick_base`)。`_note_audit_resolve` 內以 `if push is not None: ... else: _lens_push_base(...)` 分兩條(patch 中 `push=None` 參數與該分支)。`_push_mainline` 也等於第三個主線判法,與 `_mainline_ref` 並存。
2. 並存的理由與收斂路有寫,只是在圖譜:`Issues/推送前其他閘的範圍在合過主線時會多算.md` 寫明 home/note-shape 用另一套、要驗證後改用 `_push_range_start`、且有 `REVISIT:2026-10-31`;`_push_mainline` docstring 也解釋了為何候選序與跳過「被推那條」跟 `_mainline_ref` 不同。所以不算「無理由的第二套」。
3. 缺口:`_lens_push_base` 與 `_mainline_ref` 的 docstring 都沒指向新的一套,`_push_range_start` docstring 也沒說「這是要取代 _lens_push_base 的方向」。下一個改 `_lens_push_base` 的人只看程式碼,會漏改另一套(這條正是 r2 三份各有洞的成因)。屬程式碼內導覽缺口,不是行為問題,未造出翻紅重現。

## 其餘逐項判定(不影響,不列 finding)
- 參數命名:`--push-remote`、`--pushed-ref` 跟同一掛鉤裡 code-loop check 的 `--branch`/`--at-sha`(`scripts/lumos:37751`)是不同型別(這裡是完整 ref、遠端名),沒有同義重複到造成錯用的場景;`--diff A..B` 沿用既有 `dr_diff`。
- `pp_stop_if_signaled`:掛鉤內所有「rc1 擋、其他放行」的閘共五道(home check、note-shape、spec-gate、code-loop check、drift)全走同一支,`pre-push:346-480` 已無第二種寫法;`impact`、`bound-tests --advisory` 等本來就 `|| true` 的不是這型,不算漏。
- CI 步驟:新步驟結構(`rc=$?`、rc1 印 `::error::`、其餘 `exit "$rc"`)與同檔 code-loop、note-shape 兩步一致(`.github/workflows/ci.yml` 該區塊)。
- 呼叫層次:掛鉤只呼叫 `lumos drift check`,沒有跨層直呼工具內部函式。

最高等級:minor
