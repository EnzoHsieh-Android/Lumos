severity: minor

## 通才回歸席報告(第三輪)

整體判斷:這次修補沒有弄壞既有功能。四組指定測試全綠,我另外跑的相關子集也全綠。我找到三個小問題,都不擋推送。

### 測試結果
```
-k contract     87 passed, 0 failed
-k backing      41 passed, 0 failed
-k disposition 110 passed, 0 failed  (t_codeloop_check_dispositions_gate 最慢 90.0s,餘裕只有 2x,工具標了「餘裕不足 3 倍」)
-k handoff      55 passed, 0 failed
```
補跑的子集:`-k spec_freeze` 73 passed、`-k dispatch_lens` 312 passed、`-k help_when` 2 passed,都是 0 failed。

### Finding

severity: minor
blocking: 否 — 照舊手冊操作會被 rc 2 擋下,錯誤訊息直接給出正確路徑,不會靜默做錯事
引句:「派工詞要附圖譜鏡頭 | 在計劃所在的工作樹跑」
問題:`--out` 改成只收 `governance/review-reports/` 底下,而且計劃在別的工作樹時不帶 `--out`。lumos-design-loop 的三份手冊和 `--help` 文字都改了,但 lumos-project-notes 的兩處還是舊寫法。
- 第一處是 `commands/05-設計審查迴圈.md` 第 31 行,寫「在計劃所在的工作樹跑 `lumos spec-freeze <計劃.md> --out <rN-snapshot.md>`」。
- 第二處是 `reference.md` 第 83 行,同樣寫 `spec-freeze <計劃> --out <rN-snapshot.md>`。

`t_design_loop_manuals_spec_freeze_wording` 只讀 `skills/lumos-design-loop/` 底下的三份,沒讀這兩處,所以守衛抓不到。
具體失敗情境:我在暫存庫實跑 `lumos spec-freeze docs/kg-knowledge/Projects/p_計劃.md --out r1-snapshot.md`,得到 rc=2、`out_outside_repo`。不帶 `--out` 才 rc=0 並印出 `LUMOS-SPEC:` 那一行。照 project-notes 手冊做的人第一次一定會被擋。
佐證:
- file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:31`
- file: `skills/lumos-project-notes/reference.md:83`

severity: minor
blocking: 否 — 本 repo 與 workspaces 底下 14225 篇筆記實測零篇受影響,只是對其他專案的潛在退步
引句:「if not _LENS_SPEC_NODE_NAME_RE.fullmatch(node) or node.startswith」
問題:`_vault_node_path` 現在要求節點名整段符合節點名字元集(只收 ASCII、CJK、`_ . / -` 與空白,最長 80 字)。落點與計劃連結因此共用這條規則。
- 全形括號、全形冒號、`+`、`&` 這類合法檔名,即使會談目錄裡真有那篇,現在也只計入「含不收的字元,沒列名也沒讀」,固定席拿不到該節點的內容。
- 上一輪對「計劃來源」那行路徑已經放寬(300 字、不套字元集),理由是全形括號也是合法檔名。節點名這邊沒照同一個理由處理,兩處不一致。

具體失敗情境:中文專案有 `[[Systems/設計（舊）]]` 這類連結時,設計審派工詞少了該節點。
佐證:file: `scripts/lumos:49345`

severity: minor
blocking: 否 — 屬於資安修補的有意收窄,但沒有逃生口也沒有提示
引句:「符號連結的 *-knowledge 不算(代碼審 code-派工鏡頭可指定目標repo r2 資安1」
問題:`*-knowledge` 資料夾或 `docs/` 上層是符號連結時,行為比 base 嚴。
- 工作樹寫法回 `no_knowledge`。
- 提交寫法下,`_vault_dir_ok` 讓所有節點都被當成「指到圖譜外面」。
- 說明行只寫「連結寫法不合或指到圖譜外面」,看不出是資料夾本身是符號連結。

具體失敗情境:有人把共用圖譜用符號連結掛進 `docs/` 時,設計審的固定席整段消失,而訊息沒有指出原因。這是我推測的使用場景,本機沒有實例。
佐證:
- file: `scripts/lumos:49301`
- file: `scripts/lumos:49327`

### 已讀,無 finding
- `--out` 改選填:
  - 讀了 `_spec_freeze_check_out` 與 `_spec_freeze_finish`。`out=None` 時回 `(None, None)`,`fail()` 一律回 rc 2,沒有把成功 rc 0 誤判成失敗的路徑。
  - 絕對路徑、從子目錄執行、macOS 的 `/tmp` 對 `/private/tmp` 都由 realpath 比對處理。
  - 提交寫法的辨認分界(冒號前全十六進位、至少 7 碼)與 dispatch-lens 一致,一般路徑不會誤入。
- 測試執行器存回入口環境:
  - `_LUMOS_ENTRY_ENV` 正好是 `lumos` 入口(`scripts/lumos:53205` 起)改動的四個變數,存回清單與入口一致。
  - 只影響測試行程,不影響 lumos 本身。
- 掛鉤改照 `spec_source` 判:
  - 比對 base 提交,base 的 `lumos` 完全沒有 `spec_source`。對舊版 lumos 而言,以前「代碼不在計劃類集合」與現在「沒有 `spec_source`」都回空字串,結果相同。
  - 範圍路徑(`rng` 非空)根本不走 `_spec_fail_note`。串列或物件型別的 `lens_fail` 已由型別先判擋掉,不會再崩在 unhashable。
- `_repo_walk_lstat` 換掉原本的逐段檢查:
  - 對照舊版,三件事都等價:最後一段是符號連結時 `S_ISREG` 為假、中間不存在回 `None`、`--out` 最後一段留給 `_spec_freeze_out_ok`。
  - `_spec_freeze_lstat`、`_spec_freeze_out_path`、`_vault_dir_ok` 三處共用,語意一致。
- `_dispositions_verdict` 還原後表態閘:
  - 只加了 `deadline is not None and` 這個保護。
  - `_disp_record_for` 本來就處理 `None`,唯一的呼叫者也一定傳期限。base 該處沒有保護,所以這是變嚴謹,不是退步。
  - 110 條表態測試全綠。
- 拿掉 `ls-tree -r`:
  - `cat-file --batch-check` 輸入與輸出一行對一行,候選已排除換行與 NUL。
  - 符號連結(120000,在 `cat-file` 裡也是 blob)由第二步 `ls-tree` 的 mode 擋掉。
  - NFC 比對兩邊一致。
  - 候選一律是 `(kind, 路徑)` 單純字串,沒有被當成 git 旗標的路徑。
  - 批次 200 個路徑的迴圈有逐批檢查期限。
- `cmd_dispatch_lens_spec` 的順序調整(落點先於 impact)與 `_nodehome_landing_sizes` 的新回傳(只剩標題就回空)互相一致。

最高等級 minor,blocking 0 條。
