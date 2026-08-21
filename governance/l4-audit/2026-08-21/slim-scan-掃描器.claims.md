C1. FLOW 順序：讀交付檔(README/SKILL.md/reference.md)逐行掃 → 真值取 `lumos --help` 解析出的指令全集減 KEEP 白名單得 removed 集合 → 五種形態各自 regex 對照 → 命中彙整成候選清單(不改檔、只印) → rc 0/1/2 | 預期驗證點: 掃描器主流程 main() 的步驟順序與 exit code 分支

C2. removed 集合的真值來源是 `lumos --help` 解析出的 choices（非硬編清單），KEEP 白名單共 26 支保留指令、寫死在腳本內 | 預期驗證點: 掃描器腳本內 KEEP 白名單常數，條目數為 26

C3. KEEP 白名單於 2026-08-11 納入 delguard、於 2026-08-16 納入 query | 預期驗證點: KEEP 白名單變更歷史（git log / commit 訊息含對應日期與指令名）

C4. 五種懸空引用形態：①prefixed（`lumos <cmd>` 帶前綴）②bare-token（反引號裸 token）③skill-name（DROP_SKILLS 清單含簡稱如 design-loop/code-loop）④span-with-args（反引號內帶參數如 `loop status --gate`，與②共用同一 regex，靠 span==first 判斷是②還是④）⑤prose（裸散文，無反引號無前綴直接嵌句子） | 預期驗證點: scan_line() 函式內對應五種形態的分支/regex 定義

C5. 形態⑤裸散文比對有 `len(cmd) < 4: continue` 短路——短於 4 字元的指令名（如 `gov`）不比對散文形態 | 預期驗證點: scan_line() prose 分支內的長度判斷程式碼

C6. 2026-07-31 Task 5 修正形態⑤ prose 假陽性：原邊界 `(?<![`\w\-])cmd(?![\w\-])` 未排除路徑分隔 `/` 與副檔名 `.<ext>`；修法為後顧多排 `/`、前瞻多排 `(?!\.\w)` | 預期驗證點: scan_line() prose 正則表達式的原始碼（修正前後對照）

C7. 掃描器新增 `--python` 旗標：以 ast 掃描 `ast.Constant` 的 str，套用同一套 scan_line() 形態比對，不掃程式碼識別字/註解；檔名為 `.py` 副檔名的檔案會自動走此模式（供合成 fixture 用） | 預期驗證點: 掃描器內 scan_python_file() 函式定義與 --python CLI 旗標及副檔名自動判斷邏輯

C8. 真世界審計對產物 CLI（`dist/scripts/lumos`）實測，字串常數共 11 處指向已移除指令：init/update/self-audit/gov/anchor/canary | 預期驗證點: t_slim_scan_python 測試斷言內容或對產物實際掃描的輸出

C9. `_windowed_text(s, token, width=120)` 函式：先在正規化後字串裡找 token 位置，以該位置為中心各留約半個 width 的窗口，超出邊界加 `…` 標記；找不到 token 時退回開頭截斷 | 預期驗證點: 掃描器內 _windowed_text() 函式定義

C10. 第二輪修正後 `scan_line()` 改為回傳 `(token, form, pos)` 三元組，各形態在判定當下自行回報觸發位置：prefixed 用 `m.start(1)`、backtick 系用 `m.start(1)+content.find(first)`、skill-name 用 `line.find(s)`、prose 用 `m.start()` | 預期驗證點: scan_line() 函式回傳值型別與各分支 pos 計算程式碼

C11. `scan_python_file()` 與 `main()` 的呼叫端改為先正規化字串（`" ".join(s.split())`）再餵給 `scan_line()`，使比對與開窗共用同一份字串座標系 | 預期驗證點: scan_python_file() 與 main() 內對輸入字串呼叫 `.join(.split())` 正規化的程式碼

C12. 回歸測試 `t_slim_scan_window_centered`（scripts/test_lumos.py）：造一段填充文字 > 120 字、命中詞（`lumos gov`）排在填充文字之後的合成 docstring，斷言 `text` 欄位包含該命中詞 | 預期驗證點: scripts/test_lumos.py 內 t_slim_scan_window_centered 測試函式內容

C13. 測試 `t_slim_skill_reference_scan_assertions` 掃描 `slim/skills/lumos-project-notes/{SKILL.md,reference.md}`，用 (檔名, 行號, token, form) 四元組精確白名單比對；候選共 22 條，其中 21 條是已審自我揭露句、1 條（reference.md:342 的 `install` prose）是已審查假陽性（講的是 `npx playwright install`） | 預期驗證點: scripts/test_lumos.py 內 t_slim_skill_reference_scan_assertions 的白名單條目數與內容

C14. `t_slim_scan` 測試對 skills/lumos-project-notes/{SKILL.md,reference.md} 真實掃描得 candidates=129；filename 假陽性修正後對同批檔案與 slim/skills/lumos-project-notes/{SKILL.md,reference.md} 重跑，candidates 數不變（129/14） | 預期驗證點: scripts/test_lumos.py 內 t_slim_scan 與 t_slim_scan_filename_fp 斷言的候選數字

C15. 執行 `python3 scripts/test_lumos.py -k slim` 全量 121 passed、0 failed | 預期驗證點: 該指令的實際測試輸出（passed/failed 計數）
