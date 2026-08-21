C1 [❌] kind 實際有三選項 caught|missed|none，非僅 caught|missed | 證據: scripts/lumos:14246 `cr.add_argument("kind", choices=("caught", "missed", "none"))`；--loop/--severity/--auditor/--token/--note 旗標本身核對無誤(14247-14252)

C2 [✅] loop/severity 皆採「有給才寫鍵」邏輯，未給則不寫入該鍵 | 證據: scripts/lumos:3210-3211 `if loop: rec["loop"]=loop`；scripts/lumos:3231-3232 `if severity: rec["severity"]=severity`

C3 [✅] loop status 為唯讀查詢，--need 預設 None→2，讀 .canary-log.jsonl 依 append 序（非 ts 排序） | 證據: scripts/lumos:4288-4289(argparse default=None)；scripts/lumos:4329-4330(need=2)；scripts/lumos:4320 docstring「讀 .canary-log.jsonl 的 append 序(不 ts-sort)」；scripts/lumos:4368-4379(逐行 append 序 parse，未依 ts 排序)

C4 [❌] 「預設（panel）模式」的稱呼有誤——預設（未帶任何模式旗標）走的是 legacy tail-K 分支(scripts/lumos:4460-4481)，與顯式 --panel 觸發的 _loop_status_panel(scripts/lumos:3634 起，round 分組+cluster 邏輯)是完全不同的兩條路徑；且判準本身也對不上：good() 實際判準是 `kind in ("caught","none")`（非僅 caught）且 `severity in (clean,minor)` | 證據: scripts/lumos:4460-4461 `def good(r): return r.get("kind") in ("caught", "none") and r.get("severity") in ("clean", "minor")`；scripts/lumos:4463 `converged = len(rounds) >= need and all(good(r) for r in rounds[-need:])`；panel 為互斥旗標見 scripts/lumos:4296(`ls.add_argument("--panel", ...)`)

C5 [✅] 篩選為 `d.get("loop") == loop_id` 嚴格等值 | 證據: scripts/lumos:4378 `if d.get("loop") == loop_id:`

C6 [✅] 缺 severity 視同未收斂，non-clean 處理正確（good() 要求 severity 落在 {clean,minor}，None 不在集合內） | 證據: scripts/lumos:4460-4461；回歸測試 scripts/test_lumos.py:3623-3625 "loop status: 缺 severity → 未收斂"

C7 [✅] 記錄數<K（含 0 筆）回傳未收斂、exit 1 | 證據: scripts/lumos:4463-4476（converged=False 時走 else 分支 `rc=1`）；scripts/test_lumos.py:3608-3609 "loop status: 無記錄 → exit 1"

C8 [✅] `need = max(1, need)`，小於 1 的值被夾到 1，不視為參數錯誤（無對應 rc2 分支） | 證據: scripts/lumos:4361 `need = max(1, need)`（此行前無 need<1 的 ERROR/return 2 判斷）

C9 [✅] 非 --gate 輸出格式：首行 status 字串，接著每輪一行 tab 分隔 `順位\tkind\tseverity\tts\tnote` | 證據: scripts/lumos:4477-4478 `print(f"{i}\t{r.get('kind', '?')}\t{r.get('severity', '-')}\t{r.get('ts', '')}\t{r.get('note', '')}")`（注：--gate 模式欄位不同，多插入 findings 欄，見 scripts/lumos:4563，此為 claim 未涵蓋範圍）

C10 [✅] exit code 語意：0=CONVERGED、1=未收斂(含無記錄)、2=真錯誤 | 證據: scripts/lumos:4471-4476(0/1)；scripts/lumos:4326-4327,4334-4335,4343-4344,4358-4360 等多處 `return 2`（argparse 外的手動參數校驗與 IO 失敗)；scripts/lumos:4380-4382(`OSError` 讀檔失敗 → return 2)

C11 [✅] cmd_gov canary mapper 中 `loop=` 前綴確實放在 detail 組裝字串最前段（second 專屬前綴例外），且後續輸出有 `[:50]` 截斷 | 證據: scripts/lumos:3010 `+ (f"loop={d['loop']} sev={d.get('severity', '?')} · " if d.get("loop") else "")`（位於 verdict 前綴之後、auditor+note 之前，一般 record 無 verdict 前綴時即為最前段）；截斷見 scripts/lumos:3041,3072 `r['detail'][:50]`

C12 [✅] --settle 收斂判準為「清單全結清 ∧ G1 ∧ G3」，且與 --panel/--light/--need/--min-seats 互斥（rc2） | 證據: scripts/lumos:4312 `print(f"✅ SETTLE GATE PASS ({loop_id}: 清單全結清 ∧ G1 ∧ G3)")`；互斥檢查 scripts/lumos:4342-4351(對 panel/light/need/min-seats 均 return 2)

C13 [❌] settle 模式「caught 輪」實際定義是 `kind in ("caught","none") ∧ auditor 非空`，非僅 `kind=caught ∧ auditor 非空`（claim 漏了 none；程式碼內部舊 docstring 4218 行文字本身仍寫「kind=caught」但緊鄰的實作與新註解 4263-4264 已改收 none，此為程式碼內部新舊註解不一致，以實作為真值） | 證據: scripts/lumos:4265-4269 `def is_caught_round(n): ... return r.get("kind") in ("caught", "none") and bool(r.get("auditor"))`；對比舊 docstring scripts/lumos:4218 「kind=caught ∧ auditor 非空」

C14 [✅] --disposal 收斂判準為四條合取（G3 hash 鏈 ∧ 處置集合重算[互斥+聯集+blocker不得accepted] ∧ 留痕 sha 重驗 ∧ quote-check 引句全錨定），canary caught/missed 不計入合取，且與 --panel/--light/--settle/--need/--min-seats 互斥 | 證據: scripts/lumos:9386-9390(docstring 四條)；9437-9450(①G3)；9451-9478(②處置集合，含 9466 FO&AC 互斥、9468 FO|AC!=F 聯集、9472-9473 blocker+accepted 擋)；9480-9535(③留痕重驗+④quote-check)；9536-9542(canary 觀測「不進合取」)；9548(PASS 訊息四條字串)；互斥見 scripts/lumos:4331-4336；測試 scripts/test_lumos.py:14187 `def t_loop_status_disposal_gate()`

C15 [✅] 設計理由（append 序優於 ts 排序：ts 僅精確到秒、同秒無法定序，append 序唯一且天然反映時間先後）與程式碼註解一致（決策節點本身在圖譜、依規則不讀，僅能核對程式碼側佐證，理由文字吻合） | 證據: scripts/lumos:4320 docstring「讀 .canary-log.jsonl 的 **append 序**(不 ts-sort:ts 只到秒、同秒會並列)」；scripts/lumos:3207 canary record 端註解「隨機,非時間戳(同秒不撞)」佐證同一秒多輪的已知現象

✅10 ❌3 ❓0 ⏭0
