severity: major

(審材 a=scripts/lumos patch、b=測試 patch 逐 hunk 讀過;重現一律在 `git clone --shared` 的臨時目錄,用測試檔自帶的 `_df_repo` / `_df_fix` 造 vault 跑 `drift fix`。)

## F1 `--keep --dry-run` 照樣寫入表態檔
severity: major
blocking: 是
引句:「return cmd_drift_ack(env, rel, line, "c2", o["reason"])」
佐證: file: `scripts/lumos:28072`(cmd_drift_fix 的 keep 早退);`scripts/lumos:27829` 附近 `_drift_fix_args_err` 不把 dry_run 列入互斥檢查
1. 輸入:`lumos drift fix Issues/K 3 --kind c2 --keep --reason "還沒解決啦" --dry-run`(K 是連著已收尾計劃的 open Issue,第 3 行是 c2)。
2. 走到 cmd_drift_fix:參數檢查過(dry_run 不在 `_DRIFT_FIX_OPTS`)→ `_drift_fix_target` → 命中 `kind == "c2" and o.get("keep")` 直接 `return cmd_drift_ack(...)`,`o["dry_run"]` 從頭到尾沒被看。
3. 重現輸出:rc=0,印「✓ 表態記下了(DACK-96d89147)」,`governance/drift-acks.jsonl` 從無到有(`(root/"governance/drift-acks.jsonl").exists()` 為 True)。
4. 壞在哪:`--dry-run` 的說明與計劃承諾是「不寫筆記、不寫帳」,這裡寫了表態,而表態會讓該筆發現被視為已處理(c2 在推送閘與 scan 裡靜音),使用者以為在預覽卻已豁免了一筆。測試 t_drift_fix_refuses_wrong_kind 的 ⑨ 只驗 `--close --dry-run`,沒有 `--keep --dry-run` 案例,所以沒被抓到。

## F2 c4 `--new` 含成對引號或 YAML 標記字元時,寫出真 YAML 解析不了的 frontmatter,而自驗照過
severity: major
blocking: 是
引句:「if (t.startswith(("-", "#")) or ": " in new or t.endswith(":") or " #" in new or new.count('"') % 2」
佐證: file: `scripts/lumos:27867`(`_drift_c4_text_err`);`scripts/lumos:27935` 附近 `_drift_fix_c4` 的 check 用同一個 parse_frontmatter 算 after 再比對(自己比自己)
1. 輸入 A:valid_under 是被雙引號包住的項目(`  - "本工作樹(未提交)"`),`--old "(未提交)" --new '已提交 "abc" ok'`。引號個數為偶數,過了「成對以外的引號」檢查。
2. 寫出:`  - "本工作樹已提交 "abc" ok"`;rc=0、回報成功、修復帳照記。用 PyYAML `safe_load` 讀這一段得 ParserError(Ruby Psych 也是 SyntaxError)。
3. 輸入 B:`valid_under: 本工作樹(未提交)`,`--old "本工作樹(未提交)" --new '*alias'`。過檢查(只擋開頭的 `-`、`#`),寫出 `valid_under: *alias`,PyYAML 報 ComposerError undefined alias。其他 YAML 標記開頭(`!`、`&`、`%`、`@`、反引號、`|`、`>`)同理沒擋。
4. 壞在哪:工具號稱「不寫出一份會壞的筆記」,但判斷「換完之後結構有沒有壞」用的是 lumos 自己寬鬆的 parse_frontmatter,對照它自己 parse 出的 `after`,所以不可能翻紅;其他吃這份 frontmatter 的工具(Obsidian、外部 YAML 解析)會整篇讀不出來。原本 `--new` 的引號規則沒考慮「被換的位置本身在引號字串裡」。

## F3 c2 結案橫幅在沒有 H1 的 Issue 裡會插進程式碼圍欄內
severity: minor
blocking: 否
引句:「h = next((i for i, ln in enumerate(body) if ln.startswith("# ")), None)」
佐證: file: `scripts/lumos:27749`(`_drift_close_banner`)
1. 輸入:Issue 正文一開頭就是 ``` 圍欄,圍欄內有一行 `# comment`,之後才有 `[[Projects/Done_計劃]]`,沒有任何真正的 H1。
2. `_drift_close_banner` 用 `startswith("# ")` 找標題,沒看圍欄狀態,把圍欄裡的 `# comment` 當標題,橫幅被插在它後面。
3. 重現輸出:檔案變成 ``` / `# comment` / 空行 / `> 已結案(…)…` / 空行 / ```,橫幅跑進程式碼區、原有的圍欄內容被改。rc=0,自驗照過。
4. 範圍很窄(需要沒有 H1 而且圍欄內有 `# ` 開頭的行),故 minor。同函式在 c3 的 `_drift_append_note` 有用 `_visible_lines` 判圍欄,c2 沒有對等處理。

## F4 修復帳/表態帳讀取用 splitlines,U+2028、U+0085、換頁字元會把一筆 JSON 劈成兩半,tool 自己讀不回自己寫的那筆
severity: minor
blocking: 否
引句:「for ln in raw.decode("utf-8", errors="replace").splitlines():」
佐證: file: `scripts/lumos:27492`(`_drift_jsonl_rows`);`scripts/lumos:8507` `_jsonl_append_verified` 以 `ensure_ascii=False` 寫、以 `for line in f` 讀回(只在 \n 切,所以自驗照過)
1. 輸入:先用 `--new "甲(已提交 abc)"` 修同一篇 valid_under 的第 1 項(`_drift_c4_text_err` 只擋 `\n`、`\r`),接著修第 2 項。`--reason` 含 U+2028 的 c2 也同樣;筆記原本被改的行若含換頁字元也會。
2. 寫帳時 `changed` 裡的 after 帶 U+2028 原樣落盤;`_drift_jsonl_rows` 用 `str.splitlines()` 切,U+2028 被當換行,該筆兩半都不是合法 JSON 被略過。
3. 重現:`_drift_fix_last_sha(...)` 回 None、`_drift_next_seq(...)` 回 1(該筆 seq 本該是 1、下一筆應為 2);第二次 `drift fix Verification/E 6 --kind c4 ...` 回 2,訊息「有未提交的改動(不是 drift fix 自己留下的)」,而對照組(不含 U+2028)照計劃 ⑦ 能連修兩項。
4. 影響:乾淨檢查認不出工具自己的改動,同一篇一項一項修的流程斷掉,seq 重號;要先提交才能繼續。`_drift_load_acks` 也是 splitlines(舊碼),表態的 text 若含這些字元同樣被吃掉。

## F5 帳檔路徑錯誤在筆記已寫入之後才發現,留下「改了筆記、沒帳、且工具拒絕重跑」的半完成狀態
severity: minor
blocking: 否
引句:「err = err or _drift_fix_write(env, cx, res) or _drift_fix_verify(env, cx, res)」
佐證: file: `scripts/lumos:28085`(寫筆記在前);`scripts/lumos:27573` 附近 `_drift_ledger_path_err`(符號連結、硬連結數、解析後路徑)只在 `_drift_fix_record` 裡才呼叫
1. 輸入:`governance/drift-fixes.jsonl` 是符號連結(或硬連結數不是 1、上層目錄是符號連結),對一篇乾淨、有追蹤的 Issue 跑 `drift fix ... --kind c2 --close --status done --reason ...`。
2. 這些條件在寫筆記之前就查得出來,但檢查放在第 7 步:第 5、6 步已經把筆記改好。
3. 重現輸出:rc=2,「擋下:… 是符號連結」與「筆記已改好,但修復帳沒記到」;`git status` 顯示該篇 ` M`;再跑同一指令得「有未提交的改動(不是 drift fix 自己留下的)——先提交或還原再修」(帳裡沒這筆,指紋對不上)。
4. 可用 git checkout 還原,故 minor;但可預檢的錯誤留到寫入後,使用者得靠訊息裡的指示自己收拾。

## F6 被修的筆記本身是符號連結時,連結被換成一般檔
severity: minor
blocking: 否
引句:「atomic_write_verify(cx["path"], res["new"], res["key"], res["check"])」
佐證: file: `scripts/lumos:28022`(`_drift_fix_write`);對照 `scripts/lumos:27573` 帳檔有查符號連結,筆記側沒有
1. 輸入:`Issues/Link.md` 是指向 `Real.md` 的符號連結(git 追蹤、乾淨),`drift fix Issues/Link 3 --kind c2 --close --status done --reason 已經修好了`。
2. 乾淨檢查以 `git diff --quiet HEAD` 過(連結本身沒變),讀檔跟著連結,寫入走 atomic replace 把 `Link.md` 換成一般檔。
3. 重現輸出:rc=0、`os.path.islink(Link.md)` 變 False、`Real.md` 沒動(仍是 open);git 看到的是 120000→100644 的型別變更,不是內容修改;`Real.md` 之後仍是 c2。硬連結那條(`Hard.md` 另有一個硬連結)寫完後兩邊內容分岔,同理。
4. 工具對帳檔嚴格擋符號連結與硬連結,對被改的筆記完全沒有同樣處理,行為不一致;只影響少數把筆記做成連結的庫,故 minor。

## 已驗過、沒問題的邊界(不算 finding)
- --close/--keep 都給或都沒給、`--keep --status`、`--close --status pending`、c3 `--status pending`:都在 `_drift_fix_args_err` 擋下。
- `--reason` 3/4/200/201 字與多行:`_drift_fix_reason_ok` 用 strip 後長度 4–200、拒 `\n` `\r`,邊界正確。
- `--old` 出現 0 次、2 次:回 2 並列行號;不含那三個詞:擋。
- 檔尾沒換行的 Issue、沒有 H1 的 Issue(c2)、空正文(c3):都寫出合理結果(見測試與我的重跑)。
- 同名多篇、路徑含 `/` 但不存在:`_drift_fix_target` 擋。BOM、CRLF:`load_raw_for_edit` 拒(測試 ⑧ 已涵蓋)。
- 未追蹤檔:乾淨檢查擋;seq 是字串、布林:`_drift_ack_seq` 視為 0。

## 圖譜鏡頭固定席逐條判定
- guard-kill([[Systems/guard-kill]],★INVARIANT★ rc 優先序、--json 純度):diff 沒碰 guard kill 的 rc 邏輯與 JSON 輸出,不影響。
- lumos-cli-read(search 預設排除 superseded):diff 沒動 search,不影響。
- lumos-cli-lifecycle(re-inject 只動 sentinel 之間):diff 沒動 re-inject / CLAUDE.md 寫入,不影響。
- bound-tests-gate(code-loop check 逐支真跑綁定測試):diff 新增測試不改閘邏輯;新增的 `_BOOKKEEPING_FILES` 條目只放寬簿記豁免,不影響閘判定,不影響。
- 授權與歸屬(授權檔不得進 _VENDORED_TOOLKIT、主程式檔頭 SPDX+MIT):diff 沒動檔頭與白名單,不影響。
- 測試假綠形態(還原翻紅釘要配前置斷言):新測試多數有前置斷言(例:①前置);但 F1 顯示 `--keep --dry-run` 路徑沒有任何測試,屬覆蓋缺口,不是違反該合約。
- design-loop(處置閘第五步):diff 不動處置閘,不影響。
- pitfalls-code-loop(★RISK★):新增 `drift-fixes.jsonl` 進 `_BOOKKEEPING_FILES` 與既有表態檔同表,不影響風險分級邏輯。
- 其餘只列名的節點(loop-convergence-recording 等):diff 不碰其程式區段,不影響。

最高等級:major
