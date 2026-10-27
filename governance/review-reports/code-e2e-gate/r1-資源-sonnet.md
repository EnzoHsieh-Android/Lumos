severity: minor

整份 diff 逐 hunk 讀完。我造了大輸入實測,找到 5 條小問題,沒有會擋實作的。

## Findings

**1. 判定的 60 秒預算管不到純 Python 迴圈,大改動會被擋成「git 太慢」**

severity: minor
blocking: 否

file: `scripts/lumos`,`_e2e_gate_owners` 迴圈與 `_e2e_owners`,diff 第 1379~1391 行。

引句:「        got = _e2e_owners(f, feats)」

- 場景:`_e2e_gate_need` 對每個改到的檔呼叫 `_e2e_owners`。每次都重跑 `_e2e_norm`,走遍所有功能的 `paths`,再走遍所有情境的 `flows`,工作量是檔數 × (功能數 + 情境數 × flow 數)。
- 這個迴圈沒有 `_secev_deadline_check`,第一個「對不到任何功能」的檔出現後也不提早結束。
- 重現:用 `git fast-import` 造分支,200 個功能 × 5 個情境,10 萬個樹內檔,改 2 萬檔,跑 `lumos android-e2e check`。
  - 總時間 8.7 秒。cProfile 顯示約 2390 萬次 `_e2e_norm`,佔 31.5 秒 / 35.9 秒(含 profile 開銷)。
- 放大一級:20 萬個樹內檔、500 個功能 × 10 個情境(5000 條 flow)、改 10 萬檔。
  - 跑了 115 秒,預算是 60 秒。
  - 結果是 `blocked`、`code:"timeout"`,理由寫「git 太慢或檔案樹太大」。
  - 真正耗時的是這個迴圈,迴圈跑完後下一次 git 呼叫才丟 `_SecevTimeout`。正常推送被擋,訊息還指錯原因。
- 同一類成本:`_e2e_fingerprint` 的 `ls-tree` 把 `dirs[2]`(全部 flow)當 pathspec 傳給 git,所以每支 flow 都會拉長 ls-tree。在 20 萬檔的樹上:
  - 100 條 flow 0.66 秒,500 條 1.27 秒,2000 條 3.9 秒,5000 條 8.9 秒。
  - 不帶 pathspec 整棵列只要 0.32 秒。
  - 這道判定每個 ref 要對兩端各列一次,docstring 說「上萬檔的 repo 不整棵列」,在 flow 多時反而比整棵列慢。
- 小規模無感:10 萬檔改動、100 個功能的 r1 場景整道只要 3.2 秒。

**2. 開場掛鉤一份壞紀錄就讓全部 AI 放行提醒消失,超過 500 份後第 501 份起也看不到**

severity: minor
blocking: 否

file: `scripts/hooks/claude/lumos-entry-hook.py`,`_e2e_ai_line`,diff 第 719~742 行。

引句:「        for p in sorted(d.glob("*.json"))[:500]:」

- 場景 A,例外沒有逐檔隔離:`json.loads` 在 `for` 迴圈裡,`except Exception` 包在整個函式外。
  - 兩台機器同時改同一份紀錄,git merge 留下衝突標記的 `<指紋>.json`,迴圈就整個跳出,回傳 None。
  - 巢狀過深(`RecursionError`)也一樣。
  - 重現:同一目錄放 1 份有 AI 放行的合格紀錄和 1 份內容為 `<<<<<<< HEAD…` 的紀錄,`_e2e_ai_line` 回 `None`。刪掉壞檔後正常印出「有 1 筆…」。
  - doctor 的 `_e2e_records_all` 有逐檔回報「紀錄讀不懂」,掛鉤沒有,兩邊不一致。
- 場景 B,500 份上限依指紋排序:這個順序跟時間無關。造 600 份紀錄,AI 放行放在排序最後那份,掛鉤回 `None`,耗時 3.5 秒。同一目錄下 doctor 用的 `_e2e_ai_pending_all` 找得到。
- 場景 C,時間上限只有份數和單檔大小,沒有總時間:每份紀錄約 1MB 時,500 份要 3.5 秒;單檔上限 2MB 時依比例約 7 秒。

**3. doctor 的 AE 段讀全部紀錄,沒有份數、大小、時間上限**

severity: minor
blocking: 否

file: `scripts/lumos`,`_e2e_records_all` 與 `_e2e_ai_pending_all`,diff 第 1680~1695 行。

引句:「    for p in sorted(d.glob("*.json")) if d.is_dir() else []:」

- 場景:紀錄每個指紋一份,只增不刪、進版控。
  - `waive --list`、`--ack`、doctor 的 AE 段都對每份做 `_e2e_load_json`(`_events_depth_ok` 加遞迴 `_e2e_fix_surrogates`)和 `_e2e_record_err`,沒有上限。
  - 重現:600 份、共約 600MB 的紀錄(每份 history 約 9000 筆),`_e2e_ai_pending_all` 花 44.8 秒,約每 MB 75 毫秒。
- 現實量級較小:3000 份 × 20KB 約 60MB,估計約 4~5 秒。
- 掛鉤自己有 500 份、2MB 的上限,doctor 這邊沒有同樣的保護。

**4. 讀提交樹裡的 blob 是先全讀進記憶體、再比單檔上限**

severity: minor
blocking: 否

file: `scripts/lumos`,`_e2e_tree_blob`,diff 第 1246~1259 行。

引句:「    if len(raw) > _SECEV_FILE_MAX:」

- 場景:先 `cat-file blob` 把整個內容經 `capture_output` 讀進記憶體,之後才比 16MB 上限。
  - 單次 git 上限是 20 秒,擋不住大小。
  - 重現:被推送提交裡 `.lumos/macrobench.json` 是 400MB 的 JSON,`lumos android-e2e check` 回「超過單檔上限」,峰值記憶體 1.36GB(`/usr/bin/time -l`),約 3.2 倍。
  - 查證紀錄和主線候選的 macrobench.json 走同一個函式。
- 既有基礎建設有先問大小再讀的做法:`_nodehome_cat_sizes`,`_secev_mainline_override` 就在用。這裡漏了先問 `cat-file -s`。
- 輸入是被推送提交裡的檔案,作者可控。

**5. 治理帳事件帶整份情境清單,沒走 `_gate_event_fit` 的 4096 位元組政策**

severity: minor
blocking: 否

file: `scripts/lumos`,`_codeloop_e2e_step`,diff 第 1925~1941 行。

引句:「extra={"fingerprint": rep.get("fp"), "commit": marker_sha, "cases": rep.get("cases") or [], "code": rep.get("code")})」

- 場景:`blocked` 和 `passed-by-feature` 兩種事件,`cases` 是這次要驗的全部「功能.情境」。
  - 直接交給 `_gate_event_or_warn` 寫進進版控的 `docs/.governance-log.jsonl`。
  - 重現:500 個情境的專案,一次 `_codeloop_e2e_step` 寫出約 7.4KB 的一行。
  - 5000 個情境約 75KB 一行。被擋後每次重試推送都再追加一筆。
- 專案自己的 `_gate_event_fit` 就是把帳行壓在 4096 位元組、必要時截尾並記 `_truncated`。其他閘有套用,這條沒有。
- 連帶:`_cl_say_e2e_block` 的 `todo` 沒像 `bad_cases` 那樣只取前 10 筆,`--case` 建議指令會印出全部情境。

## pitfalls manifest(pitfalls-builtin 兩條)

- `scripts/lumos:41707`(`open(` 資源類):這是 `_E2eRecordLock.__enter__` 的 `os.open`,`os.write` 外面有 `try/finally os.close(fd)`,fd 一定關。
  - 若 `os.write` 失敗(磁碟滿),鎖檔會留下空檔,下一次進來 5 秒後被接手。自癒,不算問題。誤報。
- `scripts/lumos:41733`(`time.sleep` 效能類):`_stale_or_wait` 的 0.2 秒 sleep 受 `self.wait`(預設 60 秒)限制,最壞等 60 秒。
  - 屬於鎖的等待,是併發題,判範圍外。誤報。

## 其他資源問題(逐項看過,沒事)

- 子程序回收:`_lens_git` 用 `subprocess.run(timeout=…)`,逾時和 Ctrl-C 都會殺掉子程序再往外丟。`_e2e_gate_evaluate` 不攔 `KeyboardInterrupt`。
- `_confirm_tty_stdin` 逾時回 None 行為正確。`LUMOS_TTY_TIMEOUT` 這個測試接縫已存在。
- 不用 E2E 的專案單 ref 成本:16 次 git 呼叫,約 0.29 秒(用本 repo 實測),可接受。

## 圖譜鏡頭

- `Issues/code-loop守衛main-direct盲區`:不影響。pre-push 只多一個 `android_e2e` 種類和逃生句。`_codeloop_e2e_step` 排在所有放行早退之前,從 `raw_range` 取起點,走的是 `_secev_mainline` 的主線判法,沒有重開盲區。
- `Systems/存量漂移守衛`、`Systems/每支檔有家`、`Systems/筆記內容閘`:不影響。沒有新增程式檔,也不碰漂移檢查本體。
- `Systems/lumos-cli-lifecycle`(★INVARIANT★ re-inject):不影響。掛鉤只多印一段提醒,沒碰 CLAUDE.md 的 sentinel 區塊。
- `Systems/lumos-cli-read`(★INVARIANT★ search):不影響。diff 沒改 search。
- `Systems/pitfalls-code-loop`(★RISK★):不影響既有行為。新增 `android_e2e` 這個擋下種類,`_codeloop_kg_finish` 已把它的明細鍵加進來。
- `Systems/guard-kill`(★INVARIANT★ 兩條):不影響。沒碰 guard kill 的 rc 優先序或 `--json` 純度。
- 「這次新增的殘留」段:這份提示尾端沒有出現。

## 實驗清理

臨時目錄 `/private/tmp/lumos-seat-work/code-e2e-gate/資源-sonnet/` 已用字面絕對路徑刪除。

最高等級是小問題;擋實作的 0 條,共 5 條
