C1 [❌] main() 實際順序是先算 removed 集合、才逐檔讀行掃描，非主張所述「先讀檔逐行掃→才取 removed 集合」 | 證據: scripts/slim-scan.py:154(`removed = all_commands(...) - KEEP` 在迴圈之前)、:156(`for fp in a.files:`)、:164(讀檔逐行在 removed 算完之後才發生)；rc 0/1/2 部分正確(:176 `return 1 if out else 0`，2 見 :46/:160)

C2 [❌] removed 集合來源非硬編、真值取自 `--help` 屬實，但 KEEP 白名單現況為 27 支非 26 支（2026-08-19 新增 update 後未反映） | 證據: scripts/slim-scan.py:34-36（實際切出 27 個詞，含 08-19 新增的 `update`）；git log 顯示 275f381（Aug 19）新增 update 使總數從 26→27

C3 [✅] delguard 於 2026-08-11 入列、query 於 2026-08-16 入列，兩者皆屬實 | 證據: git log 453ed5d(Tue Aug 11 10:09:55 2026, "delguard 入列") 、3bae3cb(Sun Aug 16 02:07:21 2026, "slim KEEP 收編 query 25→26 支")

C4 [✅] 五種形態(prefixed/bare-token/skill-name/span-with-args/prose)定義與②④共用同一 regex、靠 span==first 判斷，皆與程式碼相符 | 證據: scripts/slim-scan.py:62-64(prefixed)、:68-76(bare-token/span-with-args，`"bare-token" if span == first else "span-with-args"`)、:80-83(skill-name/DROP_SKILLS :29-31)、:91-96(prose)

C5 [✅] 形態⑤有 `len(cmd) < 4: continue` 短路，註解明講排除 gov 這類短詞 | 證據: scripts/slim-scan.py:92 `if len(cmd) < 4:          # 太短的詞(如 gov)誤報率過高,交給形態 1/2`

C6 [✅] 2026-07-31 Task 5 修正 prose 正則：原邊界未排 `/` 與 `.<ext>`，修法為後顧多排 `/`、前瞻多加 `(?!\.\w)` | 證據: scripts/slim-scan.py:94 現況正則、git show fe9f6538 (Fri Jul 31 17:54:21 2026, commit msg 含"Task 5(公開精簡版實作計畫最後一個 Task)")：`-(?<![\`\w\-])cmd(?![\w\-])` → `+(?<![\`\w\-/])cmd(?![\w\-])(?!\.\w)`

C7 [✅] `--python` 旗標走 ast 掃 `ast.Constant` 的 str、套用同一套 scan_line()、`.py` 副檔名自動判斷 | 證據: scripts/slim-scan.py:121(def scan_python_file)、:134(`isinstance(node, ast.Constant) and isinstance(node.value, str)`)、:136(呼叫 scan_line)、:148-151(--python CLI 旗標)、:161(`if a.python or p.suffix == ".py":`)

C8 [❌] 主張「共 11 處指向 init/update/self-audit/gov/anchor/canary」是舊版測試 docstring 內容(scripts/test_lumos.py:15938-15939)，但對現況產物實測(--python 模式)得 candidates=38、tokens={anchor,canary,code-loop,design-loop,gov,impact,init,install,refcheck,remove,self-audit,signoff}，`update` 因已入 KEEP 不再命中，數字與內容皆已過期 | 證據: 實跑 `python3 scripts/slim-gen.py --outfile /tmp/slimaudit/lumos && python3 scripts/slim-scan.py --python /tmp/slimaudit/lumos --json` → total=38，tokens 不含 update；scripts/test_lumos.py:15959 註解自承「update 2026-08-19 自期望移除:已入 slim-scan KEEP」

C9 [❌] 主張函式簽名為 `_windowed_text(s, token, width=120)`(自己找 token 位置)，實際簽名為 `_windowed_text(norm, idx, token, width=120)`，直接吃呼叫端算好的 idx，函式 docstring 明講「不得自己重猜命中位置」，與主張所述行為(先找 token 位置)相反 | 證據: scripts/slim-scan.py:100 `def _windowed_text(norm, idx, token, width=120):`、:103-107(docstring 明講不自己 `.find(token)`)

C10 [✅] scan_line() 回傳 (token, form, pos) 三元組，各形態自報位置：prefixed 用 m.start(1)、backtick 系用 m.start(1)+content.find(first)、skill-name 用 line.find(s)、prose 用 m.start() | 證據: scripts/slim-scan.py:64(prefixed)、:74-76(bare-token/span-with-args)、:82(skill-name)、:96(prose)

C11 [✅] scan_python_file() 與 main() 呼叫端皆先 `" ".join(s.split())` 正規化再餵 scan_line() | 證據: scripts/slim-scan.py:135(`norm_val = " ".join(node.value.split())`)、:165(`norm_line = " ".join(line.split())`)

C12 [✅] t_slim_scan_window_centered 造 >120 字填充文字、命中詞 `lumos gov` 排在填充文字之後的合成 docstring，斷言 text 欄位含命中詞 | 證據: scripts/test_lumos.py:15990-16017（`pad = "filler " * 30`、`pad + '跑 \`lumos gov\` 才對'`、`check("★視窗置中★ text 欄位包含命中詞 gov...")`）

C13 [❌] 主張「候選共 22 條，21 條自我揭露+1 條假陽性」，實際 reviewed 白名單只有 18 條(17 自我揭露+1 假陽性 install/prose@343)，實跑掃描 slim/skills/lumos-project-notes/{SKILL.md,reference.md} 亦得 total=18 | 證據: scripts/test_lumos.py:18052-18073(reviewed 集合逐條數共 18 項，含 :18070-18072 的 install/prose 假陽性)；實跑 `python3 scripts/slim-scan.py slim/skills/lumos-project-notes/SKILL.md slim/skills/lumos-project-notes/reference.md --json` → total=18

C14 [❌] t_slim_scan(scripts/test_lumos.py:15898) 與 t_slim_scan_filename_fp(:15964) 都是用小型合成 fixture(6 行/3 行)驗證形態命中與假陽性排除，並未對 skills/lumos-project-notes 或 slim/skills/lumos-project-notes 做真實掃描、也無 candidates=129/14 這類斷言；實跑對 `skills/lumos-project-notes/{SKILL.md,reference.md}` 掃描得 total=138（非 129），且找不到任何測試對此目錄做等價比對 | 證據: scripts/test_lumos.py:15898-15931(t_slim_scan 只用 root/sample.md 合成內容)、:15964-15987(t_slim_scan_filename_fp 只用 root/sample.md 3 行 fixture)；實跑 `python3 scripts/slim-scan.py skills/lumos-project-notes/SKILL.md skills/lumos-project-notes/reference.md --json` → total=138

C15 [❌] 主張「121 passed、0 failed」，實跑 `python3 scripts/test_lumos.py -k slim` 得 69 個測試案例(「lumos 測試(69 案例)」)、474 個 check() 斷言 passed、0 failed，兩種計數口徑皆非 121 | 證據: 實跑輸出「lumos 測試(69 案例)」開頭、結尾「474 passed, 0 failed」，exit code 0

✅8 ❌6 ❓0 ⏭0
