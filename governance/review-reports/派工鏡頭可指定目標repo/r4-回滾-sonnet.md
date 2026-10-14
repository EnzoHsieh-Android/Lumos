severity: major

第四輪「版本錯開與回退」席。實驗用的暫存目錄已刪。

## 已讀,無 finding 的節

- **新舊掛鉤與新舊全域 lumos 混用**:實測舊 lumos 收到 `<sha>:docs/...` 這種值,stdout 空、stderr 一行、rc 2,跟計劃第 10、回退第 4 條的描述一致。讀掛鉤原始碼,舊掛鉤的 `_fail_note` 在沒有範圍時回空字串,新 lumos 的失敗 JSON 不會讓它出錯。多出來的 `spec_commit` 欄位,`seat-check` 也不挑。
- **不掛分支的提交被 gc**:在實驗 repo 做了 `commit-tree` 的不掛 ref 提交,`git gc --prune=now` 之後 `cat-file` 讀不到,跟計劃第 9、實務隱患的描述一致。預設兩週的窗口沒問題。另外 `commit-tree` 不吃 `commit.gpgsign`(實測 rc 0),沒有簽章把 spec-freeze 弄失敗的疑慮。
- **回退第 2 步**:舊 lumos 對 `spec-freeze` 回「擋下:沒有「spec-freeze」這個指令」,核對句可行。

---

severity: major
blocking: 是 — 計劃自己給的 gc 後復原步驟,在計劃已被修改過時會悄悄換掉已凍結的快照,破壞「一輪只凍一份」。
引句:「重跑 spec-freeze 即可」
問題:第 9 條的 spec-freeze 會「原子寫進 `--out`」。拒絕條件只列了路徑含空白、不合路徑規則、不是一般檔、沒有 HEAD,沒有「`--out` 已存在且內容不同」。每輪派工前本來就要敲一次 spec-freeze,實務上也常為補派逾時的席再敲一次。計劃在實務隱患裡把提交被 gc 或同一輪重派的復原法寫成「重跑 spec-freeze」,而編排者照慣例會在收完席報告後立刻把修正折進工作樹的計劃。
具體失敗情境:
1. 第 N 輪凍結 `rN-snapshot.md`(blob A)。
2. 該輪途中提交被清掉(或編排者要補派一席),鏡頭回 `spec_rev_missing`。
3. 此時工作樹的計劃已被折入修正(blob B),編排者重跑 `lumos spec-freeze <計劃> --out rN-snapshot.md`。
4. spec-freeze 用 blob B 建新提交,並覆寫 `rN-snapshot.md`。
5. 先前各席的 `quote-check --spec <凍結快照>` 全部對不上,同一輪出現兩個 blob、兩份快照。這正是「邊審邊折會 hash 分裂」的老問題,而且這次是工具自己造成的。

建議:`--out` 已存在且 blob 不同時拒絕,除非明確加旗標;或第二次執行只許重建同一個 blob(`hash-object` 一致才放行)。
佐證:計劃第 9 條步驟;file: `/tmp/派工鏡頭可指定目標repo-r4.md:82`、`:140`。

---

severity: minor
blocking: 否 — 回退當下才碰到,現行提交檢查會多挑一次錯,補好即可。
引句:「免得 doctor 到期叫人去數一個已不存在的欄位」
問題:回退第 5 步建議的 `[closed:<日期> 已回退]`,理由只有 3 個字。現行 `_revisit_closed` 要求結案理由至少 4 個實字。實測 `[closed:2026-10-20 已回退]` 回 `結案理由至少 4 個字`,`已回退不做` 則通過。
具體失敗情境:回退時照步驟 5 寫 `已回退`,那行被判成「結案標記寫錯」。結案沒生效,doctor 到期還是會唸。要在回退的緊急提交裡重改,還得再多跑一輪提交前檢查。
佐證:file: `scripts/lumos:37782`(lens-repo 唯讀目錄)。

---

severity: minor
blocking: 否 — 只影響回退後「回到原狀」的核對是否完整,運作中不會壞。
引句:「把那個來源拉到還原後的提交」
問題:有兩個缺口。
- (a) 步驟 3 與核對只看 `~/.claude/hooks/dispatch-lens-hook.py`。`_sync_global_hooks` 也會把同一批 hook 檔 copy2 到 `~/.codex/hooks/`,本機該目錄確實存在,回退核對沒列。
- (b) 步驟 3 要靠消費專案跑 `lumos update` 才會同步全域 hook。但 `cmd_update` 在專案根就是來源 repo 時只重刷紀律區塊、不同步全域 hooks。若機器上沒有可成功 pull 的消費專案,全域掛鉤就留在新版,得改跑 `lumos install`,計劃沒提。
具體失敗情境:退完後只核對 `~/.claude/hooks` 的指紋就宣布回原狀,`~/.codex/hooks` 仍是新掛鉤(Codex 只走領席路徑,影響小,但「回到原狀」的宣稱不成立)。
佐證:file: `scripts/lumos:24961`(`_sync_global_hooks` 對 claude 與 codex 兩家 copy);file: `scripts/lumos:23153`(root 等於 src 的分支),另見 `:24307` 起的 `cmd_update`。

---

severity: minor
blocking: 否 — 只發生在回退當下仍有進行中迴圈時,有手動補救,但補救本身會讓固定席對不上凍結版本。
引句:「還有派工詞帶著提交寫法的進行中迴圈」
問題:回退第 4 條承認舊 lumos 會靜默不附,也不會有說明行,卻沒給找出這些迴圈的辦法。計劃只說派工單多記 `spec_commit`,沒說去哪掃。補救是 `lumos dispatch-lens --spec <工作樹路徑>`,而舊 lumos 讀的是工作樹現況、不是凍結快照。這跟新設計要解決的「讀的是沒凍結的工作樹內容,快照與鏡頭對不上」是同一件事。
具體失敗情境:回退後下一輪編排者還沿用上一輪貼的 `LUMOS-SPEC: <sha>:<路徑>`,所有席靜默拿不到固定席,這正是整案要消除的症狀。就算手動補,內容也已和 `rN-snapshot.md` 不同版本。
建議:回退步驟加一條 `grep -l spec_commit governance/review-reports/*/r*-dispatch.json` 當清單。

---

severity: minor
blocking: 否 — 現況只是少了測試,沒有已知壞掉的路徑。
引句:「提交寫法照常能用,只少 note 與失敗說明行」
問題:計劃把「舊掛鉤配新 lumos」「新掛鉤配舊 lumos」寫成版本錯開時的保證,還說兩邊版本錯開是常態。驗收條款 S1–S18 沒有任何一條拿舊版掛鉤檔(例如基準提交的 `dispatch-lens-hook.py`)去跑新 lumos,也沒有拿新掛鉤去跑舊 lumos。我讀原始碼確認舊掛鉤這條路目前沒有問題,但這個宣稱沒有東西守著。改到 `_fail_note` 簽名或掛鉤重試邏輯時,不會有測試翻紅。
佐證:file: `scripts/hooks/claude/dispatch-lens-hook.py:250`(`_fail_note` 簽名,計劃要改);file: `scripts/hooks/claude/dispatch-lens-hook.py:456`(只對 `--role-cards`、`--arch-target` 重叫)。

---

severity: minor
blocking: 否 — 計劃已用 REVISIT 承認,且範本寫了 `lumos spec-freeze` 降低機率,但偵測要等 11-15。
引句:「有就讓 spec-freeze 比對自己與」
問題:這個專案的 CLAUDE.md 與測試慣例都教人敲 `python3.14 scripts/lumos`,也就是專案那份。若編排者照習慣用專案那份跑 `spec-freeze`,專案那份是新版,印得出 `LUMOS-SPEC: <sha>:<路徑>`,但掛鉤叫的是 `_trusted_lumos` 找到的全域 lumos。全域 lumos 若還是舊版,會把它當工作樹路徑,rc 2、stdout 空,靜默不附。這就是整案要消除的靜默放空,只是搬到另一個口。
理由:第 10 條「產得出那一行就代表全域 lumos 認得」只在編排者敲的是 PATH 上那支時成立。spec-freeze 本身可以便宜地擋掉這條:跑時用 `_trusted_lumos` 的邏輯找出全域那支,和自己不是同一檔就警告。計劃選擇等 5 週後數事件再說。
佐證:file: `scripts/hooks/claude/dispatch-lens-hook.py:308`(`_trusted_lumos`);file: `/tmp/派工鏡頭可指定目標repo-r4.md:88`、`:148`。

---

最高等級 major,blocking 共 1 條(spec-freeze 重跑覆寫已凍結快照);其餘 5 條均為 minor、非 blocking。
