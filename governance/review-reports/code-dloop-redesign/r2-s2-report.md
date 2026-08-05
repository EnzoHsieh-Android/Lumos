# r2-s2 對抗代碼審查報告

審查對象：`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/907f3c42-1246-4d5f-a854-ed66bb17b77e/scratchpad/codeloop/code-dloop-redesign-r2-s2.patch`（r1 修復批 delta diff）

方法：逐 hunk 讀完整份 diff，對可疑點在真倉庫（/Users/enzo/harness/lumos-toolchain）實測驗證（含把 diff 尚未落地的那段 hunk 手動套進 `scripts/lumos` 複本重現）。

---

## Finding 1 — `cmd_loop_verify_progress` 新欄位裸取 `findings_set`，缺鍵必 KeyError 崩潰（無 traceback 保護，違反本 patch 自己立的紀律）

- **severity: blocker**
- **file:line**：diff 新增於 `cmd_loop_verify_progress`（patch 內 hunk `@@ -3384,9 +3402,11 @@`，對應現行倉庫函式起點 `scripts/lumos:3363`；此欄位在**目前 working tree 尚未真的落地**——已用下方步驟把 diff 原樣套進 `scripts/lumos` 複本並實測重現，證實此改法若落地必炸）。
- 引句：「`"last_disposal_n": (len(rounds[-1]["findings_set"]) if rounds else 0),`」
- **失敗場景**：`findings_set` 是選配欄——`cmd_canary` 只在呼叫端帶 `--findings-set` 時才寫入（真代碼確認：`scripts/lumos:2806` `rec["findings_set"], ... = f_set, fo, ac` 包在 `if f_set:` 分支內）。任何 loop 的**最後一筆 record 沒帶 `--findings-set`**（例如純 `canary record caught/missed` 不帶處置帳、或 missed 席、或任何非 disposal-carrier 的一般記錄）都會撞上。而 `loop verify-progress` 明講是「獨立進度驗證器」，用途廣於 disposal loop，這是常態輸入形狀，不是邊角案例。
- **實測重現**（在真倉庫套用 diff 原文後執行）：
  ```
  $ python3 /tmp/lumos_patched --vault /tmp/vprog_repro/docs/kg loop verify-progress V --json
  Traceback (most recent call last):
    ...
    File "/tmp/lumos_patched", line 3410, in cmd_loop_verify_progress
      "last_disposal_n": (len(rounds[-1]["findings_set"]) if rounds else 0),
                              ~~~~~~~~~~^^^^^^^^^^^^^^^^
  KeyError: 'findings_set'
  RC=1
  ```
  倉庫既有測試 `t_loop_verify_progress`（`scripts/test_lumos.py:2943`）的 `rec()` helper 從不帶 `findings_set`，若這段 diff 真的落地，該測試會直接翻紅（且是以未捕捉例外/traceback 的方式炸，而不是乾淨 rc2）。
- 這正是本輪 review 要抓的「fix 引入的新洞」：同一份 patch 另外三處（quote-check UTF-8、disposal 讀側 UnicodeDecodeError、canary-log 壞行）都特別強調「FAIL 但不得 traceback」的紀律，這裡卻用裸 `[...]` 取代慣用的 `.get()`，直接違反自己剛立的規矩。
- **修法建議**：`rounds[-1].get("findings_set") or []`（比照同一行上方 `has_result_hash` 用 `in` 判存在、`findings_trend` 用 `.get()` 的既有風格）。

---

## Finding 2 — `_loop_status_disposal` 的 round-id fallback 從「每筆各自成組」改成共用常數 `"__legacy"`，無 `--round` 的多筆 record 被靜默合併成一輪，讓過期 carrier 冒充最新判定

- **severity: major**
- **file:line**：`scripts/lumos:8144`（本次 diff 已真的落地在倉庫）
- 引句：「`rid_ = r.get("round") or "__legacy"`」
- **對照舊碼（diff 刪除行）**：「`groups.setdefault(r.get("round") or f"__seq{len(groups)}", []).append(r)`」——舊碼每筆無 `round` 欄的 record 各自配一把獨立 key（`__seq0`、`__seq1`…），`latest` 永遠只含「時序上最後一筆」；新碼把所有無 `round` 欄的 record 全塞進同一把 `"__legacy"` key，`latest` 變成**該 loop 全部 legacy record 的聯集**。
- **CLI 沒有任何地方強制 `--disposal` 必須配 `--round`**（`grep "disposal.*round"` 只命中呼叫轉發那兩行），所以這條路徑是活的、可達的，不是理論上不可能發生。
- **失敗場景（已在真倉庫實測重現）**：
  1. 對某 loop 先送一筆帶 `--findings-set`（carrier）+ 留痕的 `caught` record（不帶 `--round`）。
  2. 之後對同一 loop 再送一筆**不帶** `--findings-set`（只帶留痕，滿足 T6 強制）的新 `caught` record（同樣不帶 `--round`）。
  3. 跑 `loop status <id> --disposal ...`：
     ```
     [disposal] 處置集合: ✓ — 1 條全處置(折 1/放行 0,理由齊)
     [disposal] 留痕: ✓ — 判定輪全席 4 份留痕存在且 sha256 與帳面一致
     [disposal] quote-check: ✓ — 1 條引句全數錨定
       __legacy.1	caught	minor	s1
       __legacy.2	caught	minor	s2
     ✅ DISPOSAL GATE PASS
     ```
     兩筆被合併成同一「輪」，`carrier` 用的是**第一筆（較早）**record 的處置帳，第二筆（真正較新、且本身沒有任何處置帳）被免費搭車過關。
  4. 若照舊碼邏輯，`latest` 只會是第二筆（`__seq1`），而該筆沒有 `findings_set` → `carriers` 為空 → 應該印「[disposal] 處置集合: ✗ — 判定輪無處置帳」並 FAIL（`scripts/lumos:8180-8182` 的既有邏輯）。新碼把這個本該 FAIL 的情境變成 PASS。
- 這條路徑目前沒有任何測試覆蓋（新增的 `t_disposal_gate_r1_panel_hardening` 五個子場景全部都帶 `--round`），所以全套 2288 條既有測試照樣綠燈，不會自動曝光。
- 本輪 patch 的主旨正是「堵 disposal 閘的各種繞過口」（round-id 重現守衛就是為了防止 stale round 被誤判為 latest），但這次改動在修復 round-id 重現問題的同時，副作用地讓「無 round 標籤」這條路徑的語意從「只看最新一筆」退化成「只要曾經有任一筆帶處置帳就永遠算數」——與本 patch 想堵的洞是同一類洞（stale/過期判定被當最新採信）。
- **修法建議**：無 `round` 欄的 record 維持「各自成組」（例如恢復用遞增序號、或明確禁止 `--disposal` 用在完全沒有 `--round` 的帳，要求呼叫端一律帶 `--round`），而不是共用同一把 key。

---

## 未列入 finding 的觀察（未達標準，僅記錄不計分）

- `governance/eval/canary_calibration.py` 新增的「寫後讀回自驗」（`log.read_text(...).splitlines()[-1]` → `json.loads(tail)`）若恰好在寫入被截斷（磁碟滿/進程被殺於 write() 中途）的極端情況下，讀回的 `tail` 本身可能不是合法 JSON，`json.loads` 會拋 `json.JSONDecodeError`（`ValueError` 子類）而未被捕捉，導致印出 traceback 而非乾淨的「讀回自驗失敗」訊息。此為真實但需要作業系統層級寫入中斷才會觸發的邊角，且結果仍是非 0 exit code（不會誤判成功），故未列為正式 finding，僅記錄供留意。

---

## 結論

findings 數：2　max severity：**blocker**
