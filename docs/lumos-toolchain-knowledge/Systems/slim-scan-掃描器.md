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
  DEP:scripts/lumos(--help 解析 removed 集合)｜scripts/test_lumos.py t_slim_scan
  TEST:t_slim_scan 8 checks 全綠(`python3 scripts/test_lumos.py -k slim_scan`)+ 對 skills/lumos-project-notes/{SKILL.md,reference.md} 真實跑一次驗證三個已知案例(reference.md:85 子命令全覽/reference.md:730 `loop status --gate`/SKILL.md:156 裸散文 canary)全命中,candidates=129
verified_by:
  - "[[Verification/2026-07-31_slim-scan掃描器落地]]"
---
# slim-scan-掃描器

公開精簡版交付前的文字掃描器。掃描 README/SKILL.md/reference.md 等要交給離職接手者的文件,找出還在教「精簡版已移除的指令」或「不交付的 skill」的句子,列成候選清單交人逐條裁決是否需要改寫。詳見 [[Projects/公開精簡版_實作計畫]] Task 1。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-1-brief.md`(SDD 產出,非圖譜路徑,依計畫落地於此)。
