severity: major
# r3 架構對齊席(sonnet)——棧別提問表態閘(末輪)

### A1 check 回傳結構是序列早退+單一 reason,「兩個獨立判定各自出訊息」沒交代怎麼並存
severity: major
blocking: 是——bound_tests 紅時提前 return,永遠算不到適用題;spec 未交代重構方式,實作端可能另開平行路徑。⚠ 推斷。
引句:「表態核對放在 `code-loop check` 裡，跟「tier high 缺留痕」是**兩個獨立判定**、各自出各自的三段式訊息（缺表態≠缺審查，不混用「先跑一輪代碼審」那句）」
file: `scripts/lumos:20843-20887`。

### A2 子命令名 dispositions/recall-miss 是名詞,同群組 pass/skip/check 是動詞(minor,⚠)
severity: minor
blocking: 否——cochange 群組已混用 rules/check。
引句:「一份 JSON **檔案**，以裸位置參數傳入（`lumos code-loop dispositions <檔.json>`」
file: `scripts/lumos:22319-22322`、`scripts/lumos:22303-22310`。

### A3 path:line 對 at_sha 樹驗另起爐灶,繞過既有 `_validate_repo_ref`
severity: major
blocking: 是——同一件事已有唯一入口且兩處共用;新版比舊版弱(三態→兩態)。給 `_validate_repo_ref` 加可選 at_sha 才對齊。
引句:「沒有 at_sha（本機直接叫 check）退回工作樹（借 `_validate_repo_ref`）」
file: `scripts/lumos:14946-14975`、`scripts/lumos:14977-15009`。

### A4 CJK 計數沒指名沿用哪一套既有判定
severity: major
blocking: 是——檔案裡至少三套 CJK 判定並存,且 `_el_is_cjk` docstring 明記「各寫各的是被抓過的錯」。
引句:「理由門檻（r2 邊界席 B10）：去掉空白與標點後，CJK 字元 ≥10 個，或總字元 ≥25 個」
file: `scripts/lumos:7584-7587`、`scripts/lumos:2345`、`scripts/lumos:2682`、`scripts/lumos:14255`。

### A5 `git ls-tree` 非遞迴 vs dispatch-lens 遞迴(minor,同目的)
severity: minor
blocking: 否。
引句:「先 `git ls-tree --name-only <at_sha> docs/` 解析出 `*-knowledge` 的實際 slug（同 dispatch-lens 既有做法」
file: `scripts/lumos:20168`、`scripts/lumos:20182-20186`、`scripts/lumos:3761-3838`。

前輪驗收:A1–A6 全已解(hook 只格式化/形狀語意不變/裸位置參數/直讀 repo_root/剝字串/resolve_test_refs)。
不對齊共 5 條,其中 major 3 條。
