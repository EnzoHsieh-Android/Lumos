severity: minor

審查範圍:併發與資源鏡頭,加固定席圖譜節點逐條判。實驗都在 /tmp/k 的臨時 repo 做,腳本是 `/tmp/k/bench1.py` 到 `bench4.py`,沒有動 repo。

先講沒問題的部分:
- 「用到才算」(`_NotelinesPairs.table()`)在第一層成立。乾淨推送時配對呼叫 0 次(bench4)。
- 放寬帳寫入的那一行沒有超過 4 KB。`_gate_event_fit` 量的跟 `_gate_event` 寫的是同一行,因為 `_gate_event_build` 的欄位、`head_sha`、`attempt_id` 都一樣。實寫 500、2000、5000、10000 組配對,行長是 4073、4078、4078、4083 位元組,都沒超過 4096。
- 提交前(`relaxed=None`)、`LUMOS_SKIP_NOTE_SHAPE`(在算之前就 return)和 doctor(不傳 `relaxed`)都不寫放寬帳。
- 配對失敗和有扣減不會同時寫兩筆:失敗時配對表是空的,`count` 為 0。
- `_drift_m1_fit` 改走 `_gate_event_fit` 後,逐項對過行為不變:旗標都是 `rows_truncated`,`nodes` 都是 20 條上限。
- 判定檔寫入沒有新增競態。`tail` 只是判定列多一個欄位,檔名仍是隨機 32 碼十六進位。

**K1 放寬帳截斷是平方時間**
severity: minor
blocking: 否 — 要上萬行各自減掉舊違規才會拖到秒級,一般推送碰不到
引句:「while rows and size() > 4096:」
1. 輸入:一次推送有 N 行因舊行尾補括號被減掉違規,`relaxed["pairs"]` 有 N 組。走到 `_ns_relaxed_record` 呼叫 `_gate_event_fit`,迴圈每 pop 一組就整行重新 `json.dumps` 一次。
2. 預期:截斷花線性時間。實際是 O(N²),實測 `_ns_relaxed_record` 單呼叫:N=500 為 0.04s,2000 為 0.52s,5000 為 3.19s,10000 為 12.9s,外推 2 萬約 50s。這段在 pre-push 熱路徑上,也沒有逾時。
3. 重現:`python3.14 -u /tmp/k/bench3.py 10000`。
4. `_drift_m1_fit` 原本也是這個寫法,這次抽成共用函式把它擴散到新的呼叫端。

**K2 目標版本逐篇起一個 `git show`**
severity: minor
blocking: 否 — 只有推的不是 HEAD、而且有上千篇候選時才慢
引句:「ok = _ns_append_same_context(ob, reader(b) if ob is not None else None, got)」
1. 輸入:推送頂端不是 HEAD(例如 `git push origin feature:main`),或工作目錄與頂端不同。`_nodehome_reader` 對每個候選篇走 file: `scripts/lumos:26182` 的 `git show` 子行程,序列執行。
2. 起點版本是用一次 `cat-file --batch` 批次讀的,終點版本卻是逐篇讀,兩邊不對稱。
3. 實測 `_notelines_append_pairs`:200 篇候選,頂端是 HEAD 時 0.46s,不是 HEAD 時 5.12s;1000 篇分別是 1.92s 和 24.79s,約每篇 25ms。
4. 單次 `git show` 有 20s 逾時,但整批沒有總時限。
5. 重現:`python3.14 /tmp/k/bench1.py 1000 100 nonhead`。

**K3 起點 blob 與配對表沒有總量上限**
severity: minor
blocking: 否 — 要整批筆記每行都補括號才爆量
引句:「起點版本單篇大於這個就不配」
1. 上限 512 KB 只管單篇,`_nodehome_cat_blobs_capped` 會把所有候選篇一次讀進 `r.stdout`。配對表也是每個改動行一筆。
2. 實測(`python3.14 /tmp/k/bench1.py 100 9000 head`):100 篇約 400 KB、共 90 萬行配對,用 14.9s、峰值 535 MB。300 篇用 50.3s、峰值 1.6 GB。
3. 預期有批次總量或組數上限,超過就當整批不配對,走和「單篇太大」一樣的退路。實際沒有,推送掛鉤的記憶體和時間跟改動量成線性,沒有天花板。

**K4 新的 `@@` 解析器比舊的慢 8 到 10 倍**
severity: minor
blocking: 否 — 常見小提交的絕對值很小
引句:「for ln in raw.decode("utf-8", errors="surrogateescape").split("\n"):」
1. `_notelines_parse_added` 現在包 `_notelines_parse_hunks`,每一行多走一層函式呼叫和 dict 操作。逐提交的第一層、提交前掛鉤和推送前掛鉤都在用它。
2. 實測(`python3.14 /tmp/k/bench2.py`):10 MB、5 萬個改動段的 diff,舊版 0.20s、新版 1.95s。23 MB 的單段 diff,舊版 0.29s、新版 2.12s、峰值 184 MB。1.2 MB 的 diff,舊版 0.04s、新版 0.32s。
3. `_ns_append_candidates` 再解析同一份 diff 一次,又多花 1.5 到 1.6 秒。
4. 一千個提交的範圍,每個提交 diff 都小,總和受影響有限。真正會碰到的是單一巨大提交,例如 regen 或整批 import。

**K5 一次推送多個 ref 時,放寬帳可能每個 ref 各寫一筆(⚠ 未實測)**
severity: minor
blocking: 否 — 只是帳裡出現重複行,不改判定
引句:「_ns_relaxed_record(root, base_where, tip_where, relaxed)」
1. `note-shape --diff` 在 pre-push 的逐 ref 迴圈內呼叫,見 file: `scripts/hooks/pre-push:318` 的 `read` 與 `:359` 的呼叫,迴圈到 `:522` 才結束。
2. 兩個 ref 共用尚未推上遠端的提交時,範圍重疊。每個 ref 各自重算配對、各寫一筆 `relaxed`,`pairs` 內容相同,只有 `head_sha` 不同。
3. 兩個 ref 的 `LUMOS_PUSH_ATTEMPT` 相同,但放寬帳沒有按 attempt 去重。我沒有真的起 hook 重現,所以標 ⚠。

**固定席圖譜節點逐條判**
- `Systems/lumos-cli-read.md`(search 排除 superseded):不影響。diff 沒碰 search 的濾網路徑。
- `Systems/bound-tests-gate.md`(code-loop check 逐支真跑綁定測試):不影響。diff 沒碰 `code-loop check` 與綁定測試的解析。
- `Systems/guard-kill.md`(rc 優先序與 `--json` 純度):不影響。diff 沒碰 guard kill。
- `Systems/授權與歸屬.md`(`scripts/lumos` 檔頭 SPDX 與 MIT 全文,授權檔不進 `_VENDORED_TOOLKIT`):不影響。diff 沒動檔頭,`scripts/templates/note-audit-judge.md` 也不在被複製檔的授權檢查範圍。
- `Systems/測試假綠形態.md`(還原翻紅釘要配前置斷言):不影響。diff 沒有這類測試的修改。
- `Systems/design-loop.md`(處置閘第五步):不影響。diff 沒碰處置閘。
- `Systems/reversibility-governance-ledger.md`、`Systems/pitfalls-code-loop.md`(只列名,無內容):無可判項。

最高嚴重度 minor,blocking 0 條
