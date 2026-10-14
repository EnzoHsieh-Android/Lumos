severity: major

**檢查範圍**:讀了文件修補、測試修補、代碼修補裡 `spec-freeze` 的 `--out` 與掛鉤 `_mark_event` 兩段,以及 lens-repo 的 SKILL.md、templates.md、reference.md 和計劃全文。沒有跑任何測試。

severity: major
blocking: 是 — 手冊三處對「席位該指向哪份」互相矛盾,照第 3 步做會讓席位拿到舊副本,這正是第一版修的洞
引句:「Agent、`model: sonnet`、指向工作副本(Codex 編排時的完整做法」
問題:SKILL.md 第 1 步新增「席位指向它寫出的 `rN-snapshot.md`(不指這一步先複製的副本)」。第 3 步的 `+` 行(同一個 hunk 重寫的那行)仍留著「指向工作副本」,而第 1 步剛叫人複製的副本就是 `/tmp/<編號>-rN.md`。第 3 步又說 spec-freeze 是無條件的「派工前…跑」,第 1 步卻只在「工作目錄不是會談目錄時」才用 snapshot,「工作目錄」沒有定義是 cwd 還是計劃所在處。`reference.md` 第 513 行是手冊的詳版,計劃做法 11 也點名要同改,但這次完全沒動。它仍寫「指向工作副本」,第 116 行仍寫「同時 `sha256sum <計劃節點>`」。
失敗情境:編排者照第 3 步派工,席位拿到 `/tmp/...-rN.md`。第 2 步已修過真檔,副本比 spec-freeze 凍的快照舊,席位引句在快照上錨不到,quote-check 收貨時紅。照 `reference.md` 的人會用真檔的 sha256 當指紋,和 snapshot 的 sha256 不同。
佐證:``file: `skills/lumos-design-loop/SKILL.md:20,26` ``、``file: `skills/lumos-design-loop/reference.md:116,513` ``

severity: major
blocking: 是 — 手冊最核心的情境(計劃在別的工作樹)和新增的 `--out` 限制直接衝突
引句:「`--out` 只收計劃所在 repo 裡、路徑上沒有符號連結的位置」
問題:`_spec_freeze_out_path(root, cwd, out)` 的 `root` 是 cwd 所在 repo 的根,也就是計劃那個工作樹。手冊同一行又叫人把 `rN-dispatch.json`、`rN-snapshot.md`、席報告放在 `governance/review-reports/<編號>/`,那是會談目錄的路徑。手冊沒有說這個目錄是哪個 repo 的。錯誤訊息裡才有「建議 governance/review-reports/<編號>/rN-snapshot.md」,手冊本身沒寫。
失敗情境:在計劃工作樹依手冊敲 `--out governance/review-reports/<id>/r1-snapshot.md`,快照落在計劃工作樹裡,成了該工作樹的未追蹤檔。會談目錄的 `governance/review-reports/<id>/` 沒有它,但 `canary record --snapshot` 與收貨都在會談目錄找。改給會談目錄的絕對路徑,就回 `out_outside_repo`。手冊沒寫要複製,也沒寫位元組要保持相同。另外在計劃工作樹留未追蹤檔,可能被那邊的 `git add -A` 夾帶。
佐證:``file: `skills/lumos-design-loop/SKILL.md:26` ``、``file: `scripts/lumos`(`cmd_spec_freeze` 的 `_spec_freeze_out_path(root, cwd, str(out))`,見 r2-repair-code.patch 第 880 行附近) ``

severity: major
blocking: 是 — 手冊條目掛了一支和它無關的測試,屬於假綠的綁定
引句:「"at": "skills/lumos-design-loop/SKILL.md:spec_commit」
問題:`r1-fix.json` 把 SKILL.md、templates.md、`每輪修補差異派工.md`、計劃〈實作紀錄〉四個文件條目都標 `fixed`,綁定測試全是 `t_docs_enumeration_drift`。我讀了該測試全文,它只比對治理帳數、guard kill verdict 值域、hook 生命週期對稱這類機械事實。測試裡沒有 `spec_commit`、`spec-freeze`、SKILL.md 或 templates.md 的檢查(grep 為 0)。
失敗情境:把 SKILL.md 的 `spec_commit` 整句刪掉,或把第 1 步改回「指向工作副本」,`t_docs_enumeration_drift` 照綠。RETIRE-IF 和 REVISIT 數的 `spec_commit` 就會靜默歸零。這個測試對這些文件條目的判準不夠,連「測試跟條款對得上」都談不上。再加上本輪新增的 23 條修正,計劃的 S1–S22 條款沒有新增,新行為只靠 Systems 節點的 `[test:]` 掛著。
佐證:``file: `governance/review-reports/code-派工鏡頭可指定目標repo/r1-fix.json:331-360` ``、``file: `scripts/test_lumos.py:28189` ``

severity: minor
blocking: 否 — 計劃本文與條款沒跟上,但實作紀錄的括號有補
引句:「(更正 2026-10-14 代碼審 r1:`--out` 先驗位置——照字面去掉 . 與 .. 後要在 repo 根底下」
問題:計劃做法 9 第 5 步仍只寫 `out_conflict`,第 1 步前後的失敗代碼沒提 `out_outside_repo`,條款 S18 和 S21 沒有位置驗證條款。更正只掛在實作紀錄的括號裡,而且那句開頭仍寫「上層資料夾不存在時會建」,同一行前後矛盾。測試 `t_spec_freeze_out_must_stay_in_repo` 沒有對應的 `[SN]` 條款,只靠 Systems 節點的 `[test:]` 掛著。
失敗情境:下一個讀計劃本文的 session 照做法 9 實作,會漏掉 `--out` 位置檢查。條款表也看不出這個檢查是被守住的。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭可指定目標repo_計劃.md:92-100,193` ``

severity: minor
blocking: 否 — 違反專案寫筆記規則,但不影響行為
引句:「代碼審 r1 修正(2026-10-14,23 條全折,卷證在」
問題:專案 CLAUDE.md 規定過程紀錄(哪天做了什麼、第幾輪折了什麼)不寫進筆記,留在 git 和卷證。這行實作紀錄,加上 `Systems/派工鏡頭` 和 `codex-harness` 新增段的標題與「協調者轉述」「四個分支逐字同一段」,都是輪次流水帳。「四個分支」指向別的分支,沒有卷證可查,讀者無法驗證。
失敗情境:節點變成進度日誌,下個 session 分不出哪些是還成立的規則。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/派工鏡頭.md`(r2-repair-docs.patch 新增段) ``

severity: minor
blocking: 否 — 守衛可能空轉,但目前看不出實際漏網
引句:「記事件壞掉({label})→ rc0、照附說明行、不丟例外」
問題:`bad_mark` 沒有計數器,也沒有前置斷言證明五條路都真的呼叫了 `mark`。只要某條路因為別的原因沒走到 `_mark_event`(例如「計劃失敗」那列的 body 不觸發記事件),測試照綠。這是 `測試假綠形態` 那條 ★INVARIANT★ 講的「現場走不到被測分支」。最後那條 `src.count(...) == 1` 是原始碼字串計數,不是行為測試。
失敗情境:把 `_mark_event` 的 `except Exception` 改回只接六種例外,若某一列沒走到 mark,測試不紅。
佐證:``file: `scripts/test_lumos.py`(`t_dispatch_lens_hook_mark_event_one_way`,見 r2-repair-tests.patch 第 522–541 行) ``

severity: minor
blocking: 否 — 影響面在 lumos 全部子命令,但文件只寫在派工鏡頭節點
引句:「os.environ["GIT_NO_REPLACE_OBJECTS"] = "1"」
問題:這是在 `main()` 入口改全域環境。所有 lumos 子命令及其子行程都不吃 `git replace` 和 grafts,也拿不到 `GIT_DIFF_OPTS`、`GIT_EXTERNAL_DIFF`。這個行為只寫進 `Systems/派工鏡頭` 的 PITFALL,沒寫進管入口的節點,也沒有任何一條說明它對 guard kill 或 pitfalls 的 diff 輸出有沒有影響。
失敗情境:使用者或其他子命令靠 `GIT_EXTERNAL_DIFF` 做事,行為靜默改變,沒有節點會被推到眼前提醒。
佐證:``file: `scripts/lumos`(`main()` 開頭,見 r2-repair-code.patch 第 1012–1018 行) ``

**逐項回應特別要看的幾點**
- 手冊「工作目錄不是會談目錄時…」與 `--out` 新限制不一致(見前兩條 major)。
- 派工單 `spec_commit` 欄位:SKILL.md 與 templates.md 都有寫,但寫法有出入(SKILL 說「用了 spec-freeze 的輪次再加」,templates 說無條件加記),而且沒有任何測試守(見第三條)。
- 實作紀錄補的兩處偏離:目標架構段 vault 取 `slugs[0]` 那條,我對照 `scripts/lumos` 的 `slugs[0]` 與 `cmd_dispatch_lens_spec` 說明,可以對上。記事件例外範圍那條,也和 `_mark_event` 的改動吻合。兩處本身屬實。
- 條款與測試的對應:S1–S22 名字都對得上,`[test:]` 指到的 14 個測試名都在 `test_lumos.py` 裡。缺的是新行為沒有對應條款,文件條目也沒有真正的守衛。
- 表態記錄:`py-eventloop`、`py-parallel` 等「不適用」宣稱和程式相符,我沒發現反證。

最高等級 major,blocking 3 條。
