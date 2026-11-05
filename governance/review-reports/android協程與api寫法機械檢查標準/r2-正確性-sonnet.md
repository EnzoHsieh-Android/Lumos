severity: major

以下每條都有重現步驟,或指向 `scripts/lumos`、hook 檔的具體行。我的實驗放在 `/tmp/lumos-seat-work/android協程與api寫法機械檢查標準/正確性-sonnet/`,已刪除。

**已讀,無 finding 的節**
- 範圍 1~5 和範圍 2 的規則包部分:訊息 ≤120 字的截斷、`include_test_paths` 的描述與程式一致。`ast-grep` 0.51.1 的 SARIF 在零命中時輸出空 `results`,找不到設定檔時 stdout 為空、rc=6。這兩種都符合「回退」節和 `_lint_run_and_parse` 的判法。
- 範圍 7 的「改名偵測」:未追蹤的 `mv Foo.kt Bar.kt` 在暫時索引裡配得到 R100,我重現了。

---

1. 衝突檔永遠不會被判成「衝突中」,反而被拿去掃
severity: major
blocking: 是——S5 的衝突條款依 spec 的演算法永遠不會成立,衝突標記被當程式碼掃。
引句:「改動清單用暫時索引算:複製目前索引到暫時檔、在暫時索引上 `git add -A`、`git diff --cached --find-renames HEAD`,真正的索引不動」
引句:「合併衝突中的檔(狀態 U)不掃」
- 重現:兩個分支改同一檔造成 `UU A.kt`,複製索引後在暫時索引上跑 `git add -A`。
- 結果:`git diff --cached --name-status HEAD` 只回 `M A.kt`。`add -A` 已把衝突解成第 0 階,U 狀態消失。
- 內含 `<<<<<<<` 標記的檔直接交給 `ast-grep`,仍命中兩側的 `b()!!`,所以會對衝突中的檔誤擋。
- 缺口:要偵測衝突得在 add 之前對真索引跑 `git ls-files -u`,spec 沒寫。

2. 這一輪只寫過非程式碼檔時,`--only` 為空,整個工作樹被掃
severity: major
blocking: 是——別的會談的未提交告警會擋住這個會談,違反「不碰別的會談的改動」。
引句:「檢查範圍只限這一輪逐字稿裡寫過的程式碼檔(`--only`),不碰同一工作目錄別的會談的改動」
引句:「`lint-new --worktree` 不帶 `--only` 時看整個工作樹」
- 觸發條件寫的是「逐字稿裡有寫檔動作」,不是「有寫過程式碼檔」。這個專案的常態是一輪只寫 `.md` 筆記。
- 輸入:這一輪只 Write 了一篇筆記,工作目錄裡另一個會談留了帶 `!!` 的 `.kt`。
- 走到哪:條件成立,程式碼檔清單為空,`--only` 傳零個參數。spec 沒寫空清單要跳過。常見的 `nargs="*"` 會把它當成「沒帶」,變成全樹檢查,於是 block。
- 解法方向:空清單時整道不跑。

3. 逐字稿的寫檔清單會漏掉絕大多數寫入,回到已被推翻的作法
severity: major
blocking: 是——最常見的寫法完全不響,和「審查迴圈裡就乾淨」的目標矛盾。
引句:「這一輪逐字稿裡有寫檔動作;payload 沒有 `stop_hook_active`;`LUMOS_STOP_LINT_OFF`(新增)沒設」
file: `scripts/hooks/claude/check-graph-sync.py:204`——`collect_turn_actions` 只收 `EDIT_TOOLS` 的 `file_path`。Bash 只補 `rm/mv/cp` 類。
file: `docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:21`——2026-09-18 的 KEY 記載:用 `>`、`sed -i`、heredoc 改的檔,「一輪改三支只報一支」,逐字稿量到 286 次走 shell 對 31 次走編輯工具,所以收工點名改問版本控制。
- 這則 KEY 屬線索而非合約,但它是實測。
- 輸入:這一輪用 `cat > Foo.kt <<EOF` 或 `sed -i` 寫出含 `!!` 的 Kotlin。`--only` 裡沒有這支檔,不擋。
- 圖譜那篇已經不再宣稱切得出「這一輪」。範圍 8 又走回去,卻沒交代為什麼這裡可以。

4. 切進 worktree 的會談,Stop 檢查整個靜默
severity: major
blocking: 是——使用者規定要開獨立 worktree,這是主流程。
- 輸入:會談用內建方式切進 linked worktree 後,`CLAUDE_PROJECT_DIR` 仍是主 repo(`Systems/改檔前推播.md` 的 PITFALL 已記)。
- 走到哪:逐字稿裡的絕對路徑在另一個 worktree。`is_code_file` 用 `relative_to(project_root)` 把它們全濾掉,`--only` 為空,和 finding 2 疊加。
- 對照:`impact-hook.py:748` 的 `_sibling_worktree_root` 專為此寫的;`check-graph-sync.py` 沒有這個處理,範圍 8 也沒提。
file: `scripts/hooks/claude/check-graph-sync.py:268`

5. 慢命令排在前面時,後面的規則包一條都跑不到
severity: major
blocking: 是——Android 專案的主場景(同一個副檔名宣告多條命令)會讓規則包在回合結束完全不響。
引句:「時間預算不夠而沒跑到的命令,工作樹檢查只列出、不算擋,但工作樹模式的單條保底降成 1 秒」
- 輸入:`.lumos/lint.json` 的 `kt` 為 `[detekt 命令, ast-grep 命令]`。範圍 4 是「加範本」,順序是宣告順序(`_lint_stacks_for_diff` 保持 first-seen)。detekt 冷啟動超過 14 秒。
- 走到哪(`scripts/lumos:39125` 到 `39138`):detekt 進場時剩餘預算 ≥1 秒,逾時值 `max(1, 剩餘)`,於是吃光整份預算。逾時後 `ast-grep` 的剩餘預算 <1 秒,被當成「預算不足」跳過。
- 結果:只印「沒有檢查到任何東西,不算乾淨」,rc0,hook 不擋。
- 1 秒保底只防「一條都跑不起來」,沒防慢命令餓死快命令。偏偏另一案正要讓 detekt 能被推送前閘擋。

6. 對整個工作樹 `git add -A` 的副作用不受 `--only` 和預算約束
severity: major
blocking: 是——S6 的時間上限守不住,而且任何一個壞檔都讓整道檢查靜默失效。
引句:「真正的索引不動(git 自己的 stash 也用暫時索引」
- (a) 一個不可讀檔就整道失效:
  - 輸入:工作樹有 `chmod 000` 的未追蹤檔,例如 root 擁有的建置產物,或檢查中途消失的檔。
  - 結果:`git add -A` 回 `fatal: adding files failed`,rc=128,暫時索引完全沒更新,差異清單為空。
  - 被當成環境不可用而放行,spec 沒寫這條路。
- (b) 耗時與垃圾物件:
  - 輸入:600MB 未追蹤且未被忽略的檔。
  - 結果:一次 `git add -A` 耗時 11.7 秒,而且這段不在 `--budget` 內。同時在真正的物件庫寫入約 595MB 的懸空 loose object,每輪都重算。
- (c) 與快照目錄競爭:`.lumos/lintbase-*` 在消費專案可能沒被忽略(spec 自己承認)。兩個會談同時跑時,一邊 `add -A` 掃描、另一邊 `rmtree` 快照,會觸發 (a) 的 fatal。
- 解法方向:只對 `--only` 範圍加路徑限定;或用 `git add -N`、`--ignore-errors`。

7. 「乾淨才派」與「機械已查的類別席位不報」把環境不可用也當乾淨
severity: major
blocking: 是——ast-grep 沒裝時,該類別沒有任何一層檢查,審查席還被告知不用報。
引句:「手冊要求凍結前先提交,所以用提交範圍,不用工作樹」
引句:「寫明「機械已查的類別席位不報」」
- 範圍 6 規定環境不可用 rc0。手冊判斷「乾淨」只能靠 rc 或輸出。
- 輸入:派工者機器沒裝 ast-grep。`lint-new --diff` 印「沒裝 ast-grep」並 rc0,被當乾淨,派工詞寫「機械已查」。
- 三層同時漏:審查席被告知不報;推送閘在沒裝時照既有規則自動放行並記帳;pass 也是同一判定。
- 缺口:手冊沒有區分「乾淨」和「沒檢查」,rc 也沒有區分。

8. 沒印出的列在多數情況下永遠推不出來,與 S7 矛盾
severity: major
blocking: 是——spec 切分出的實作過不了 S7 自己的條款。
引句:「命中多列時照命中字數多寡、再照表序取前三列;只有真的印出的那幾列才記「同會談講過」」
引句:「沒印出的列 應 下次還能推;同一會談同一列第二次 應 不推」
- 分工是 lumos 比對並取前三列,鉤子只印、並用既有的 `_voice_once` 過濾。但 lumos 不知道哪些列已講過。
- 輸入:一個 Write 同時命中 A、B、C、D、E 五列,字數 A≥B≥C>D>E。
- 走到哪:第一次,lumos 回 A、B、C,鉤子印出並標記。第二次(同一會談、內容相近),lumos 仍回 A、B、C,鉤子全判成講過,印零列。D、E 不會出現。
- 要滿足條款,必須由 lumos 在取前三之前先排除已講過的列。spec 沒寫鉤子要把已講過的清單傳給 lumos。
file: `scripts/hooks/claude/impact-hook.py:825`——`_voice_once` 是檢查加標記一步完成,拿不到純檢查。

9. 「去掉註解與字串字面值」沒指定做法,唯一現成函式會把真程式碼吃掉
severity: major
blocking: 是——一般英文註解的撇號就能讓強字被吞,該推的列不推。
引句:「只看寫入的新內容(Edit 的新字串、Write 的全文),去掉註解與字串字面值」
- 現成的 `_PITFALL_STRLIT_RE`(`scripts/lumos:37529`)是 Python 形的:單引號字串可以跨行。
- 輸入:寫入內容為 `// we can't cancel here\nval x = repo.flow.flatMapLatest { load(it) }\n// don't forget`。
- 跑 `_strip_string_literals` 的結果:兩個撇號之間整段(含 `flatMapLatest`)被吞成空,變成 `// we can""t forget`。強字消失,不推。
- 先剝註解的實作同樣有問題:`"http://x"; x.flatMapLatest {}` 會在 `//` 把同一行後半砍掉。
- Kotlin 的 `${...}` 模板和 raw string 也沒處理。S7 的案例都太簡單,測不到。

10. 現成的 `extract_delta_text` 對 Edit 回舊字串加新字串
severity: minor
blocking: 否——沿用會讓 S7「只出現在被刪掉的舊內容」那一條測試轉紅,屬實作疏漏。
引句:「只看寫入的新內容(Edit 的新字串、Write 的全文)」
file: `scripts/hooks/claude/impact-hook.py:417`——`Edit` 的 parts 是 `[old_string, new_string]`,`MultiEdit` 同理。
- spec 沒寫要另寫只取新字串的抽取。
- 另:Edit 的 `new_string` 常是片段,會從註解或字串中段開始,剝除前沒有補上下文。

11. 「Codex 拿不到寫入內容」與現有程式矛盾
severity: minor
blocking: 否——只是 Codex 這版不推,但理由是錯的。
引句:「Codex 的改檔工具拿不到寫入內容,這一版不推」
file: `scripts/hooks/claude/impact-hook.py:70`、`:87`——`extract_patch_paths` 說明 `apply_patch` 的 `tool_input.command` 是 patch 全文。
- 新增行以 `+` 開頭,可取得。範圍 9 的前提不成立,應改寫成「這版不做」,而不是「拿不到」。

12. 暫時索引的位置在 linked worktree 裡不是 `.git/index`
severity: minor
blocking: 否——spec 沒指定怎麼找,照字面實作在 worktree 裡會讀不到。
引句:「複製目前索引到暫時檔、在暫時索引上 `git add -A`」
- 輸入:linked worktree,`.git` 是檔案,`git rev-parse --git-path index` 指到主 repo 的 `.git/worktrees/<名>/index`。
- 有 `core.splitIndex` 時,索引旁的 `sharedindex.*` 也不會跟著複製。
- 影響:失敗走環境不可用而放行。

13. ⚠ `pass` 在 pitfalls 失敗時可能整段不跑
severity: minor
blocking: 否——判不準,取決於共用函式是否沿用 keep-going 分流。
引句:「把推送檢查裡「新增告警」與「表態」兩段抽成一支共用函式」
file: `scripts/lumos:67865`——非 keep-going 時 pitfalls 失敗會在 3.5、3.6 之前 fail-open 回傳,只有 `keep_going` 才在 `kg.lint_on_pf_fail` 補跑新增告警。
- 若 `pass` 沿用無旗標路徑,pitfalls 一出錯,新增的機械檢查就等於沒有。spec 沒寫 `pass` 要不要用 keep-going。

14. 擋停原因沒有長度與數量上限
severity: minor
blocking: 否——只影響可讀性。
引句:「兩道都要擋時把兩段原因合成一則 decision:block,各自的名額各自記」
file: `scripts/hooks/claude/check-graph-sync.py:934`——既有 `stop_block_reason` 把整段限制在 ≤1500 字,因為續做提示超過約 2500 tokens 會被截成頭尾預覽。
- 新原因列出每條告警,沒有上限。一次 Write 帶出幾十條新增告警時會被截斷。
- 既有的圖譜那一段在合成時也會被擠壓。

15. ⚠ `--only` 的路徑形式與「檔不在工作樹」的輸出沒定義
severity: minor
blocking: 否——判不準,取決於實作怎麼正規化路徑。
引句:「`--only` 給了就只看那幾支」
- 逐字稿給絕對路徑,差異清單是相對於 repo 根的路徑。若專案目錄是符號連結(macOS 的 `/tmp` 與 `/private/tmp`),字串不相等就變成零檔。
- `--only` 指到沒有改動、或不存在的檔時,走既有 `no-files` 狀態。S5 只定義了「全部命令沒跑到」才印「不算乾淨」,這種情況印什麼沒寫。

---

**逐條判計劃牽連的節點是否被破壞**
這次附的五個落點節點(`Systems/linter精選目錄`、`Systems/棧別提問表態閘`、`Systems/pitfalls-code-loop`、`Systems/graph-sync-coverage`、`Systems/改檔前推播`)都登記為 0 條合約。我讀了它們的 PITFALL、KEY、RULE 行。
- `Systems/改檔前推播` 的 worktree PITFALL:範圍 9 有帶到 worktree 修法,不衝突。範圍 8 沒帶,見 finding 4。
- `Systems/graph-sync-coverage` 的 2026-09-18 KEY(逐字稿清單漏寫入):被範圍 8 的設計重蹈,見 finding 3。
- 其餘三個節點不影響。理由:範圍 4 只加宣告範本。範圍 10 沒動留痕有效性判定,只在 `pass` 前加兩道檢查。

總結:最嚴重 severity 是 major,共 15 條,其中 blocking 是 9 條(findings 1~9)。
