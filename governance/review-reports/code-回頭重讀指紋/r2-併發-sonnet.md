severity: minor

## 併發與資源席報告

我另外建了合成專案實測,臨時目錄已刪。

**實測結果**
- 200 檔、20 篇候選:7.9 秒,沒逾時。
- 1000 檔、100 篇候選(每篇列 10 檔):27.7 秒,38 篇逾時退回 v1。
- 400 檔、每檔約 800KB:27.6 秒,2 篇都逾時,最高記憶體約 1.09GB。
- 逐檔 `git diff` 平均約 24ms,849 次共 20.5 秒,是預算的主要消耗。

severity: minor
blocking: 否 — 逾時方向是多提醒,不會漏。但在大改動下結果固定,預設 `block` 的推送前掛鉤會一直擋,只剩跳過環境變數可繞。
引句:「已經記過新版紀錄的,再跑一次推送前檢查或手動 reread-check 通常就認得」
問題:`reread-prepare` 沒有截止時間,所以一定會算出 v2 並用 v2 指紋記紀錄。`reread-check` 有 30 秒上限,逾時的候選改用 v1 指紋,對不上 v2 紀錄,於是被列為「沒有紀錄」。這個結果每次都一樣,重跑不會改善,因為指紋沒有跨次快取。提示句說「通常就認得」,是錯的。
失敗情境:一條分支改了約 800 支以上被候選 about_code 列到的檔。作者跑完 prepare、記錄並提交紀錄。推送時 check 還是把逾時那幾篇列為沒對照,`block` 下每次都擋。作者照提示重跑也沒用。
佐證:
- ``file: `scripts/lumos:36413` ``(`_note_reread_fp_base`:`deadline - _NOTE_REREAD_FP_RESERVE`)
- ``file: `scripts/lumos:37483` ``(check 才設 30 秒)
- ``file: `scripts/lumos` `` 的 `_note_reread_print_layer1` 補的那句 `late` 提示

severity: minor
blocking: 否 — 單人使用、單支上限 1MB,一般專案遠不到問題量級。但這是新增的無上限記憶體路徑。
引句:「_NOTE_REREAD_FP_PREFETCH_MAX = 1024 * 1024」
問題:`_note_reread_fp_prefetch` 只限單支 1MB,沒有總量上限,也沒有支數上限。它呼叫的 `_nodehome_cat_blobs` 把整批輸出收進記憶體,又用切片複製一份。同檔案裡已有帶 `max_total_bytes` 的 `_nodehome_cat_blobs_capped`,這裡沒用。
失敗情境:約 320MB 的小於 1MB 原始檔(400 檔 × 約 800KB)讓程序常駐記憶體達 1.09GB,約為內容的 3.4 倍。支數再多,記憶體就等比放大。
佐證:``file: `scripts/lumos` `` 的 `_note_reread_fp_prefetch` 與 `_nodehome_cat_blobs`(約 31391 行)

**已讀,無 finding**
- 裸庫模式:linked worktree 下用 `--git-dir` 加 `--bare`、`-C` 到 git 目錄,實測指紋與主工作樹完全相同(`e03a5f737422329c`)。沒有暫存檔,工作目錄也不影響結果。
- 截止時間覆蓋:這次改動新增與改寫的 git 呼叫都有帶截止時間。這些呼叫是 `_note_reread_git`、`_note_reread_v2_cut`、`_note_reread_tip_names`、`_note_reread_fp_sizes` 和預取。預取逾時只會退回逐支讀,不會卡住或漏掉。
- 逾時方向:v2 退回 v1、`_note_reread_own_fps` 在過期時回空集合,都只會多提醒。
- `_note_reread_hunk_tags`:往前掃是線性的,`_NOTE_REREAD_DEF_RE` 沒有災難性回溯風險。
- `_note_reread_v2_cut` 每篇候選各跑一次 `-U0` diff,沒有快取。1000 檔的實測佔 2.4 秒(約 9%),可接受。

最高等級 minor,blocking 0 條。
