# r1 對答案審查:spec 逐條 vs diff

spec:`docs/lumos-toolchain-knowledge/Projects/Codex行為精修_計劃.md`
diff:`governance/review-reports/code-codex-refine/r1-snapshot.patch`(9 檔)

## 已實作

1. argv 解析 +『--harness codex』分支。diff `check-graph-sync.py` main() 開頭新增 `harness = "codex" if "--harness" in sys.argv and ...`(現行檔 line 547)。severity: clean, blocking: 否。
2. 逐字稿版本表加 0.153.2 + 有測試驗『版本表含當前版本』。`CODEX_TRANSCRIPT_VERSIONS = {"0.144.1", "0.153.2"}`(line 112);`test_lumos.py` 新測試開頭即斷言。severity: clean, blocking: 否。
3. `stop_hook_active` 為真 → 不擋,只印 stderr。`codex_stop_decision`(line 500-509)`if payload.get("stop_hook_active"): return False`;測試④驗證。severity: clean, blocking: 否。
4. session 標記檔已存在 → 不再擋(同 session 只擋一次)。`codex_stop_decision` 末行 `return not _stop_mark_path(session_id).exists()`;測試③驗證。severity: clean, blocking: 否。
5. 先印 block 再 O_EXCL 建標記檔,順序與『印完再記,建檔失敗不影響已印』一致。main() line 636-640:先 `print(json.dumps(...))` 再呼叫 `_stop_mark_write(sid)`;`_stop_mark_write`(line 516)用 `os.O_CREAT|os.O_EXCL|os.O_WRONLY` 失敗只回 False 不拋例外。severity: clean, blocking: 否。
6. reason 版面(首行固定標頭/第二行指令/檔名≤10+超過印「另 N 個」/整段≤1500字/含筆記名)。`stop_block_reason`(line 532-543);測試②⑨⑩驗證「另 4 個」與截斷。★注意:實務隱患段落明寫「檔名與筆記名一律經 `_safe_path` 消毒」,故 reason 內含『筆記放在…』『提到你改的檔的筆記』屬 spec 已預期範圍,非多做。severity: clean, blocking: 否。
7. Claude 側完全不變。main() 只把 Codex 新分支包 `try/except`(line 634-641),print stderr 那行在 try 區塊外、原封不動;測試⑥直接斷言「沒帶 --harness codex → stdout 空、stderr 提醒」。severity: clean, blocking: 否。
8. F3 路徑消毒 `_safe_path`(去控制字元/換行、只留可印字元、截160字)。line 526-529;測試⑬用夾帶 `\x1b`、`\r\n`、換行 key 的案例驗證。severity: clean, blocking: 否。
9. F4 首行標頭常數化 `STOP_BLOCK_HEAD`。line 481,測試②直接比對 `rl[0] == m.STOP_BLOCK_HEAD`。severity: clean, blocking: 否。
10. F6 session_id 缺 → 不擋(寧可漏)。`codex_stop_decision` `if not session_id: return False`;測試⑦驗證。severity: clean, blocking: 否。
11. 『hook 薄殼、邏輯進 lumos』分工的有意識偏離:整個改動只落在 `check-graph-sync.py` 一支既有厚 hook,diff 9 檔中沒有 `scripts/lumos` 或新 lumos 子命令。severity: clean, blocking: 否。
12. 整合席『四處同步』全數命中:①`check-graph-sync.py` 模組 docstring ②`docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md`(KEY 行+時機表)③`docs/methodology/圖譜即合約.md`(KEY 行、圖例四道表、Layer 1 表三處全改)④`skills/lumos-project-notes/commands/08-自動跑的.md`。四處文字一致改成「Claude 只提醒;Codex 擋一次續做」。severity: clean, blocking: 否。
13. F9 範本標題「三條鐵則」→「鐵則」,且 CLAUDE.md/AGENTS.md 同步刷新(兩檔 diff 內容逐字相同)。severity: clean, blocking: 否。
14. 改動(B)通用句本體植入 `scripts/templates/graph-discipline.md` 鐵則三尾、且不含本 repo 指令(測試⑪`"test_lumos" not in tpl"`)。severity: clean, blocking: 否。
15. 探針三點全中:`--stop-block on|off`(設 `LUMOS_STOP_BLOCK_OFF`)、`--codex-bypass-hook-trust`(預設關,`bypass_trust=False`)、結果新增 `hook_trace{hooks_fired,stop_block_seen}` 與 `thread_id`;既有斷言改成「預設不帶 bypass,旗標才加」(`scenario_probe.py` diff + `t_codex_s3_probe_codex_parser` 更新)。severity: clean, blocking: 否。
16. 誠實界線第三點:`LUMOS_STOP_BLOCK_OFF=1` 時產品碼退回 stderr,`codex_stop_decision` 第一個 if 已覆蓋。severity: clean, blocking: 否。
17. 實務隱患/相容升級:`stop_hook_active` 欄不在時 `.get()` 回 `None`→視同 False,不提早短路,行為與『當 False』一致。severity: clean, blocking: 否。
18. 實務隱患/失敗與回復:只包 Codex 新分支 try/except,`reason.strip()` 為空就不印 block、退回既有 stderr。severity: clean, blocking: 否。
19. 實務隱患/時序並行:session_id 消毒 `[^A-Za-z0-9_.-]`→`_`、截 120 字(`_stop_mark_path` line 512-513);標記目錄 7 天 lazy 清、每次進 `_stop_block_dir()` 順手清。severity: clean, blocking: 否。
20. f02 後測第一趟診斷出的根因修復:無副檔名 shebang 腳本算程式碼,`_shebang_script`(line 243-259)接進 `is_code_file`;測試⑭⑮覆蓋(含 `scripts/lumos` 本身)。這是計劃「實作紀錄」自己記載且要求驗收的修法,已對應實作。severity: clean, blocking: 否。
21. 子代理不誤傷:diff 未改動 hook 註冊(仍只掛 `Stop`),與 spec 聲稱『本 hook 只註冊 Stop,不會對子代理 fire』一致,無需程式碼變更。severity: clean, blocking: 否。
22. 驗收 1(單元測試清單)實質覆蓋:`t_codex_stop_block_once` 對驗收 1 列出的七種情境(改碼未寫回擋停 / stop_hook_active / 同 session 二擋 / 標記建檔失敗容錯 / LUMOS_STOP_BLOCK_OFF / Claude payload 不變 / 版本表含當前版本)全部有對應斷言。severity: clean, blocking: 否。
    - ⚠ 小備註(不影響裁定):實作紀錄自稱「14 條斷言」,實際數 `check(` 呼叫是 16 條(①–⑮ 共 15 條 + 開頭版本表 1 條);`docs/lumos-toolchain-knowledge/Verification/2026-09-05_Codex行為精修f02後測.md`(未進這份 diff)也記成「16 條斷言」,可見「14」只是計劃筆記手寫數字的筆誤,非程式碼縮水。

## 縮水

1. 標記目錄安全檢查缺失:spec 明寫『標記檔放 0700 目錄(讀前驗 owner uid 與 group/other 不可寫,同 `_lens_arm_dir_ok`;架構席 minor)』,但 `_stop_block_dir()`(check-graph-sync.py line 484-499)只做 `d.mkdir(...); os.chmod(d, 0o700)`,沒有比照 `scripts/lumos:17283` 的 `_lens_arm_dir_ok`(驗 `st.st_uid == os.getuid()` 與 `st_mode & (S_IWGRP|S_IWOTH)`)在讀/寫標記前驗證目錄已有的所有權與權限;`_stop_mark_path`/`codex_stop_decision`/`_stop_mark_write` 全程無 `st_uid`/`getuid`/`stat` 權限檢查。
   引句:「標記檔放 0700 目錄（讀前驗 owner uid 與 group/other 不可寫，同 `_lens_arm_dir_ok`；架構席 minor）」
   severity: minor(spec 自標「架構席 minor」), blocking: 否。

## 多做

(空)—9 檔 diff 逐一核對,沒有找到 spec 未提及的行為變更;skill 08 表格把觸發時機敘述從「Claude 工具呼叫後」訂正為「回合結束」屬既有事實的敘述精確化,不算新行為。

## 未實作

1. 改動(B)『本 repo 的具體指令 `python3 scripts/test_lumos.py -k <關鍵字>` 寫在 CLAUDE.md 區塊外自己的段落』完全查無——`CLAUDE.md` 全檔僅 54 行,`grep -n "test_lumos.py -k" CLAUDE.md` 零命中,diff 對 CLAUDE.md 只改了鐵則三那一行,沒有新增段落。結果是範本通用句「子集怎麼跑看專案自己的說明」在本 repo 指向一個不存在的段落。
   引句:「本 repo 的具體指令 `python3 scripts/test_lumos.py -k <關鍵字>` 寫在 CLAUDE.md 區塊外自己的段落。」
   severity: minor(純文件可發現性缺口,不影響擋停機制本身運作), blocking: 否。

2. ⚠ 驗收 1b / 2『f02 後組保存 hook 收到的 Stop payload 序列(含同 turn_id)與 usage、f02 實驗表進 Verification』——這份 r1-snapshot.patch 9 檔完全不含任何 Verification 筆記。repo 現況確實有 `docs/lumos-toolchain-knowledge/Verification/2026-09-05_Codex行為精修f02後測.md`,但它是 git 未追蹤檔(`git status` 顯示 `??`),不在這份 diff 快照範圍內;而且該篇內容沒有明確記「同 turn_id」與 `turn.completed.usage` token 成本,只記了耗時秒數。是否算這份 diff 的失分,判不準,交編排者裁(可能是快照時間點早於補寫,或 Verification 依規本就走另一支 commit)。
   severity: minor, blocking: 否。

3. ⚠ 實驗設計『也重跑 f01 Codex ×1 看 (B) 有沒有讓它不跑全套(單次,只當訊號)』——repo 內 `governance/review-reports/` 與 `Verification/` 都查不到 f01 重跑的紀錄或結果。同上,判不準是否屬本次 diff 範圍,標 ⚠。
   severity: minor, blocking: 否。

---

縮水+未實作共 4 條(其中 2 條標 ⚠ 待編排者裁)
max severity: minor

## 收貨正規化(編排者)
縮水 1 條(標記目錄信任檢查)+未實作 2 條(CLAUDE.md 子集指令;實驗/Verification 寫回)+⚠ 1 條:
severity: minor
blocking: 否
severity: minor
blocking: 否
severity: minor
blocking: 否
severity: minor
blocking: 否
