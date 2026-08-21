# anchor-integrity.claims.md 驗證結果

C1 [✅] approve 對 5 個錨點(runner×2 + hooks×3)重算 sha256 寫入 checked-in 的 anchor-baseline.json | 證據: scripts/lumos:9311-9317(ANCHOR_FILES 5 檔:test_lumos.py/test_autonomous_loop.py/pre-commit/pre-push/post-commit)、scripts/lumos:10109-10148(cmd_anchor_approve 逐檔 sha256 寫 payload);governance/anchor-baseline.json 實際內容含 5 筆 anchors 條目,已 checked-in(git 追蹤)

C2 [✅] verify 逐一比對現況 hash 與 baseline,mismatch 或缺檔回傳 rc1 | 證據: scripts/lumos:10088-10097(逐檔算 sha256,缺檔/不符皆 append 進 mismatches)、scripts/lumos:10108(`return 1 if mismatches else 0`)

C3 [✅] pre-push 呼叫 anchor verify 位於環境檢查(python3/lumos 存在性)之後、vault 閘門之前,無 vault 也會執行 | 證據: scripts/hooks/pre-push:29-33(環境檢查)、:38(anchor verify 呼叫)在 :142-146(have_vault 判斷/exit 0)之前,anchor 區塊不依賴 have_vault

C4 [✅] rc1 擋下 push,三選一訊息(還原/approve/--no-verify且留痕) | 證據: scripts/hooks/pre-push:38-47,訊息「1. 非刻意改動 → git checkout 還原錨點檔後重 push」「2. 刻意改錨點 → lumos anchor approve --note」「3. 確屬可接受 → git push --no-verify(留 PR diff 與缺 approve 事件的對帳痕)」

C5 [✅] autonomous-loop.sh 在每輪派 gap orchestrator 之前呼叫 anchor verify,errexit-safe 寫法 | 證據: governance/autonomous-loop.sh:87(while 迴圈起)→ :101(`if [ ! -f baseline ] || ! (... anchor verify); then`,`!`+子殼包裝對 errexit 安全)→ :131(`log "派 orchestrator..."`);每輪迴圈內順序確認在 orchestrator 派工之前

C6 [✅] loop 入口對 missing baseline 視同失敗硬擋;pre-push 對同情況僅 rc0+警示 | 證據: governance/autonomous-loop.sh:101(`[ ! -f "$REPO/governance/anchor-baseline.json" ] ||` 短路即失敗 exit 1,不論 verify 本身結果)對照 scripts/lumos:10079-10081(`if not bp.exists(): print("anchor: baseline 不存在(未啟用)…"); return 0`)

C7 [✅] anchor approve 寫入治理帳事件 gate=anchor-approve,note 顯示於 `lumos gov` | 證據: scripts/lumos:10147-10148(`_append_governance_log(v, [{"gate": "anchor-approve", "kind": "approved", ... "note": note}])`)、scripts/lumos:2988-2990(gov 的 .governance-log.jsonl mapper `"gate": d.get("gate","?")` `"detail": d.get("note","")`,anchor-approve 事件 kind="approved" 非 "warned" 不落入 advisory 折疊,detail 會印出)

C8 [✅] 錨點集合 v1 為固定列舉 5 個檔案,不含 scripts/lumos 本體 | 證據: scripts/lumos:9311-9317(ANCHOR_FILES 僅列 5 檔,無 scripts/lumos);governance/anchor-baseline.json 實際 anchors 鍵集合同 5 檔

C9 [✅] t_anchor 共 14 項 check(),涵蓋主張列舉的 8 類項目 | 證據: scripts/test_lumos.py:5026-5087(`sed -n '5026,5087p' | grep -c "check("` = 14);逐項對應:5032(無 baseline 警示)/5042+5052(approve 建檔並留痕)/5056(gov 顯示 note)/5061(改檔 rc1)/5072(缺檔 rc1)/5063-5065(--json)/5076-5082(重簽容缺)/5085-5086(--repo 解析錯 rc2)

C10 [✅] 決策採方案 A(baseline hash+顯式 approve),否決方案 B(RHB 環境硬化)與方案 C(純 diff 標記送審) | 證據: docs/design/2026-07-02-anchor-integrity.md:24(`### 方案 A(選此)`)、:28(`### 方案 B(否決 v1)— RHB 環境硬化`)、:31(`### 方案 C(否決獨立成案,精神併入 A)— 純 diff 標記送審`)

C11 [✅] 錨點集合 v1 固定 5 檔、不含 scripts/lumos,理由=自主 loop 每日迭代對象、收進 baseline 致每日 approve 盲簽疲勞;實際 baseline 確實排除 scripts/lumos | 證據: docs/design/2026-07-02-anchor-integrity.md:36(「不守 scripts/lumos 本體:它是自主 loop 天天迭代的對象,收進 baseline = 每天 approve → 盲簽疲勞」);governance/anchor-baseline.json 實測不含 scripts/lumos

C12 [✅] design-loop 3 輪,R1 因 missed 作廢不折,R2+R3 收斂,qwen endorsed,辯方 4 次挑戰全被判假 major 並駁倒 | 證據: docs/design/2026-07-02-anchor-integrity.md:5(「design-loop 3 輪(R1 missed 依規作廢不折、R2+R3 連 2 輪 caught+minor 自動收斂);辯方 4 次出動全駁倒假 major…qwen 跨家族複核 endorsed(worst=minor)」);:109-113(R1 兩條 F1/F2 皆「辯方反證」駁倒)、:124-130(R3 兩條 F1/F2 皆「辯方反證」駁倒)——合計 4 次挑戰全駁倒,與主張數字相符

C13 [✅] 實作計畫檔存在於 docs/superpowers/plans/2026-07-02-anchor-integrity.md | 證據: `ls -la` 確認檔案存在(35287 bytes,2026-07-02 修改),內容為 anchor-integrity Implementation Plan,與設計稿同步

C14 [❓] verified_by 指向 Verification/2026-07-02_anchor-integrity 節點是否存在且內容對應 | 證據: 驗證點在 docs/lumos-toolchain-knowledge/ 底下,依任務指示嚴格禁讀,無法查證

C15 [❓] DEP 關聯:anchor-integrity 與 lumos-refcheck 為「vault-free 同型」機制,是否同構 | 證據: 驗證點在 docs/lumos-toolchain-knowledge/ 底下(lumos-refcheck 節點內容),依任務指示嚴格禁讀,無法查證;唯 scripts/lumos 側可見 `cmd_refcheck` 與 `cmd_anchor_verify/approve` 皆屬 vault-free(不吃 --vault)風格指令,但節點本身內容不可讀故不判定為 ✅/❌

✅13 ❌0 ❓2 ⏭0
