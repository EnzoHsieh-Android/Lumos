---
type: system
status: done
created: 2026-07-31
updated: 2026-07-31
tags:
  - type/system
  - status/done
summary: |-
  FLOW:讀交付檔(README/SKILL.md/reference.md)逐行掃 → 真值取 `lumos --help` 解析出的指令全集減 KEEP 白名單得 removed 集合 → 五種形態各自 regex 對照 → 命中彙整成候選清單(不改檔,只印) → rc 0/1/2
  KEY:★不是自動改寫器★——裸 token/散文型形態必有假陽性(export/set/show/loop/impact 等本身是常見英文詞),故只出候選交人逐條裁,絕不自動改寫交付檔
  KEY:removed 集合真值來源=`lumos --help` 解析 choices(非硬編清單),KEEP 白名單(24 支保留指令)寫死在腳本內——精簡版指令集若變動需同步改 KEEP
  KEY:五種懸空引用形態——①prefixed(`lumos <cmd>`帶前綴)②bare-token(反引號裸 token `<cmd>`)③skill-name(DROP_SKILLS 清單含簡稱如 design-loop/code-loop)④span-with-args(反引號內帶參數如 `loop status --gate`,與②共用同一個 regex,靠 span==first 判斷是②還是④)⑤prose(裸散文,無反引號無前綴直接嵌句子)
  KEY:★DEBT★ 形態⑤裸散文比對有 `len(cmd) < 4: continue` 短路——短於 4 字元的指令名(如 `gov`)不比對散文形態,因誤報率過高;取捨=刻意放過短指令的裸散文誤引,交形態①②接住剩餘案例,已知缺口是「`gov` 這類短指令若以裸散文提及則掃不到」
  KEY:2026-07-31 Task 5 修正形態⑤ prose 的假陽性——原邊界只排反引號/字母/連字號(`(?<![`\w\-])cmd(?![\w\-])`),沒排路徑分隔 `/` 與副檔名 `.<ext>`,導致「檔名」(如 `` `./install.sh` ``、`scripts/install-hooks.sh` 裡的 `install`)被誤判成對已移除指令 `install` 的散文引用。修法=後顧多排 `/`、前瞻多排 `(?!\.\w)`(後接「.字母」視為副檔名)。修正後 [[Systems/slim-readme]] 的安裝指令由遷就掃描器的「用 `bash` 執行 `install.sh`」改回慣用的 `./install.sh`,原記在該節點的 DEBT 標記隨之解除
  KEY:★2026-07-31 終審 C1 修正★——原本只掃 markdown,從沒掃過產物 CLI 自己(交付的 `dist/scripts/lumos`)。它的 `warn()`/`print()` 字串常數一樣會教接手者跑不存在的指令(如 CLAUDE.md sentinel 損壞時建議「跑 lumos init/update 修復」)。加 `--python` 旗標:ast 掃 `ast.Constant` 的 str,套用同一套 scan_line() 形態比對,不掃程式碼識別字/註解。產物檔名(`lumos`)沒有 `.py` 副檔名,無法單靠副檔名自動判斷,故用明確旗標而非純自動偵測(`.py` 副檔名的檔案仍會自動走此模式,供合成 fixture 用)。★精度收益★:純文字逐行掃全檔(把它當 markdown 掃)會把 `# [code-loop r1 ...]` 這類內部審查註記也算命中,41 條裡 15 條是這種假陽性;ast 模式只認字串常數,收斂到 21 條(仍有殘餘噪音如 docstring 裡的審查註記字串,屬已知取捨,候選清單交人裁的哲學不變)。真世界審計實測產物字串常數共 11 處指向已移除指令(init/update/self-audit/gov/anchor/canary)。
  KEY:★2026-07-31 代碼審 minor-1 修正★——`scan_python_file()` 的候選 `text` 欄位原本是 `" ".join(node.value.strip().split())[:120]`,即「從常數字串**開頭**截前 120 字」,不是「以命中位置為中心」。真實案例:`scripts/lumos:416-417` 的 docstring 壓平後 134 字,`lumos gov` 出現在第 123 字,截斷後候選清單完全看不到命中的詞,人工逐條裁時無從判斷為什麼被標記。修法=新增 `_windowed_text(s, token, width=120)`:先在正規化後的字串裡找 token 位置,以該位置為中心各留約半個 width 的窗口,超出邊界加 `…` 標記;找不到 token(理論上不會發生)才退回開頭截斷。`scan_python_file()` 與 `main()` 的 markdown 逐行掃描路徑都改用此函式(同一類 bug,一併修——長 markdown 行也有相同風險)。回歸測試 `t_slim_scan_window_centered`:造一段填充文字 > 120 字、命中詞(`lumos gov`)排在填充文字之後的合成 docstring,斷言 `text` 欄位包含該命中詞(修正前必失敗,已用 git stash 暫時還原舊碼跑出真紅燈驗證)
  KEY:★2026-07-31 代碼審 minor-2 修正★——交付 skill 的 `SKILL.md`/`reference.md` 從來沒被任何測試餵進本掃描器,`t_slim_readme_assertions` 只掃 `README.md`。新增 `t_slim_skill_reference_scan_assertions`(`scripts/test_lumos.py`):掃 `slim/skills/lumos-project-notes/{SKILL.md,reference.md}`,對已知候選(22 條,皆在 reference.md,SKILL.md 目前乾淨)用**(檔名, 行號, token, form)四元組**精確白名單比對(★不是 README 那種較寬鬆的 (token, form) 兩元組★——四元組每條白名單只認一個確切位置,新增/搬動的懸空引用不會被舊白名單靜默放行),並額外斷言候選總數與白名單條數一一對應(防白名單有死條目而候選卻變少也不會被發現)。22 條候選中 21 條是已人工審過的自我揭露句(明講「這條指令本精簡版沒交付」)、1 條(reference.md:342 `install` prose)是已審查的假陽性(講的是 `npx playwright install` 裝瀏覽器,跟 `lumos install` 無關)
  DEP:scripts/lumos(--help 解析 removed 集合)｜scripts/test_lumos.py t_slim_scan｜t_slim_scan_filename_fp｜t_slim_scan_python｜t_slim_scan_window_centered｜t_slim_skill_reference_scan_assertions
  TEST:t_slim_scan 8 checks 全綠(`python3 scripts/test_lumos.py -k slim_scan`)+ 對 skills/lumos-project-notes/{SKILL.md,reference.md} 真實跑一次驗證三個已知案例(reference.md:85 子命令全覽/reference.md:730 `loop status --gate`/SKILL.md:156 裸散文 canary)全命中,candidates=129;t_slim_scan_filename_fp 3 checks 全綠(★假陽性修正★ `./install.sh`/`scripts/install-hooks.sh` 不命中、真裸散文 canary 仍命中);修正後對 skills/lumos-project-notes/{SKILL.md,reference.md} 與 slim/skills/lumos-project-notes/{SKILL.md,reference.md} 重跑,candidates 數不變(129/14)——確認此修正只消假陽性、不動真陽性;t_slim_scan_python(2026-07-31 新增)4 checks 全綠——生成產物後以 `--python` 掃描,斷言候選 token 至少含 init/update/self-audit 三類(`python3 scripts/test_lumos.py -k t_slim_scan_python`);t_slim_scan_window_centered 3 checks 全綠(minor-1 回歸);t_slim_skill_reference_scan_assertions 2 checks 全綠(minor-2 覆蓋,`python3 scripts/test_lumos.py -k slim` 全量 110 passed 0 failed)
verified_by:
  - "[[Verification/2026-07-31_slim-scan掃描器落地]]"
  - "[[Verification/2026-07-31_slim-skill與readme落地]]"
  - "[[Verification/2026-07-31_公開精簡版交付]]"
  - "[[Verification/2026-07-31_公開精簡版終審修復]]"
  - "[[Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復]]"
related:
  - "[[Systems/slim-readme]]"
---
# slim-scan-掃描器

公開精簡版交付前的文字掃描器。掃描 README/SKILL.md/reference.md 等要交給離職接手者的文件,找出還在教「精簡版已移除的指令」或「不交付的 skill」的句子,列成候選清單交人逐條裁決是否需要改寫。詳見 [[Projects/公開精簡版_實作計畫]] Task 1。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-1-brief.md`(SDD 產出,非圖譜路徑,依計畫落地於此)。
