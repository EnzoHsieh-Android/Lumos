severity: major

這份報告只改了格式,內容與等級沒動。改了兩處:F2 裡寫著省略號佔位的引句格式說明,已改成一般敘述;F3 的引句換成從 spec 逐字複製的一行。我也用 grep 逐一核對過,報告裡其餘 7 句引句都在 `/tmp/原生代碼審當通才席-r1.md` 裡找得到原文。

我用 Bash 在 `/tmp/lumos-seat-work/原生代碼審當通才席/流程整合-sonnet/` 手造 raw.json,餵 `lumos seat-import code-review`,再接 `report-normalize`、`quote-check`、`seat-check`,並呼叫 `_report_severities` 與 `_roster_family`。lumos-guard 擋 Bash 裡的「claude」字樣,所以沒能實跑 `claude -p`。F1 到 F3 涉及無頭會談行為的部分是讀 spec 與 `scripts/lumos` 推出來的,不是實測。

## F1 無頭 bypassPermissions 席的隔離比「跟派全新子代理一樣」弱得多
severity: major
blocking: 是

引句:「全新的無頭會談不帶編排者的脈絡,席位獨立性跟派全新子代理一樣。」

file: `skills/lumos-design-loop/templates.md:453`:指令只用 `--disallowedTools "Bash(git push:*)" "Bash(gh:*)" "Bash(git commit:*)"` 擋三個前綴,其餘全放行。

- **擋法繞得過**:這類前綴擋法只比對指令開頭。`git -C . push`、`env gh ...`、`/opt/homebrew/bin/gh`、先 `cd` 再 push 都不會被攔。`curl`、WebFetch 也沒擋。
- **複本指回本機真 repo**:我實測 `git clone --shared` 之後,複本的 `origin` 就是本機真 repo 的路徑。繞過前綴擋法的 push 會直接在真 repo 建分支。
- **沒有 lumos-guard 的保護**:`Systems/lumos-guard.md` 說它只認派工詞第一行有 `LUMOS-SEAT` 的子代理,擋掉含 `gh`、`git push`、`claude` 字樣的 Bash、限定寫檔目錄。無頭會談不是子代理,這些保護都不在。
- **複本含被審的 commit**:複本切到被審的頂端提交,裡面若有 `.claude/settings.json` 的 hooks 或 CLAUDE.md,無頭模式很可能不問信任就載入並執行(此點未實測)。被審的是「外部投稿」,這等於讓被審材料在無沙盒、全放行的會談裡跑程式。
- **自我宣稱不成立**:spec 的〈實務隱患〉寫「守衛面:處置閘、引句錨定、收貨三道全照舊;換掉的是一席找問題的人,不放寬任何判定」。但這一席的隔離確實放寬了。
- **建議**:改成白名單(只開 Read/Grep/Glob 與唯讀 git);移除複本的 `origin`;用 `--setting-sources` 之類的旗標排除複本裡的專案設定;並實測一次含惡意 hooks 的複本。

## F2 轉出來的席報告原文照抄,會讓 `canary record` 擋下或數錯條數
severity: major
blocking: 是

引句:「摘要與失敗情境原文照抄(不翻譯、不改寫)」

file: `scripts/lumos:48640`:標題直接拿摘要第一行,失敗情境整段多行貼進報告。三種結果我都實跑到了:

- **標題含等級字樣被擋**:摘要寫「Cache: major regression when x has backticks」(c1),標題變成 `## 1. Cache: major regression...`。`lumos report-normalize` 回 rc1,指出第 5 行是殘留的嚴重度寫法。`_SEV_HEADING_LEVEL_RE` 會把標題裡的「: major」、「non-major」、「— minor」都當殘留。`canary record` 的 `_report_normalize_issues` 因此 rc2,席報告就記不了帳。
  - 編排者又不准改報告,只剩改派一途。
  - 英文摘要裡出現 major/minor/blocker 這幾個字並不罕見。
  - 這條路徑在 spec 與計劃的 S1–S3 都沒測到。
- **圍欄吃掉後面的 severity 行**(c2):失敗情境裡有落單的 ``` 時,`_report_severities` 看不到後面條目的 `severity:` 行。reported 變成 1(實際 2 條),而 `quote-check` 兩條都看得到。`--findings` 填 2 會被「不能多於報告條數」擋下。
- **失敗情境夾帶 severity 行會被計入**(c3):失敗情境多一行 `severity: blocker`,`report-normalize` 判為合格,reported 變成 2(實際 1 條),帳面下限被抬到 blocker,而檔首宣告是 major。
  - 失敗情境是模型讀了被審的 diff 後寫的,屬於投稿方可影響的文字。
  - 失敗情境若多帶一行以「引句」為標籤的內容,也會多出一筆 quote-check 的引句。
- **建議**:轉換時把失敗情境放進縮排的引用區塊,或改寫行首的 `severity:`、`引句:`、圍欄標記。標題改用編號加檔案行號,不用摘要。同時為這三種輸入各補一支先紅的測試。

## F3 headless 席不是子代理,`seat-check` 與 dispatch 單怎麼寫沒交代
severity: major
blocking: 是

引句:「對帳時家族算同門,比較靠審查員名」

file: `skills/lumos-design-loop/templates.md:473` 與 `scripts/lumos:13459`(`_roster_dispatch_entries`):

- **派工單漏列的後果**:席位對帳只讀 `rN-dispatch*.json` 的 `auditor` 欄,按家族數人頭。§7.9 沒寫要把這一席加進 dispatch 單,漏列就會印 `seat_shortfall`。
- **seat-check 一律吵**:`seat-check` 的 `unreported` 看的是報告有沒有提到 dispatch 列的 materials 路徑或檔名。我拿含 `patch.diff` 與 `a.py` 的 dispatch 單跑,轉出來的報告都回 `unreported 1`。這一席從沒收到過 materials,每輪必然吵一次。
- **Codex 編排的迴圈會誤判**:`_roster_family("原生審查-sonnet","codex")` 回 `('external', False)`。Codex 編排時它被算成外家,鏡頭5 的同門缺額會印 `seat_shortfall`,同時像多派了一席外家。
- **spec 的說法站不住**:上面那句只在 claude 編排時成立。
- **建議**:§7.9 補寫這一席的 dispatch 條目(`materials` 留空走 vacuous 豁免,或指定為凍結 patch),並聲明 Codex 編排時此席的家族算法。

## F4 轉換直接寫進卷證目錄,違反「席報告收齊前不落地」
severity: major
blocking: 是

引句:「再用一支轉換指令把它的結果變成 Lumos 收得下的席報告」

file: `skills/lumos-design-loop/templates.md:455`:第 3 段指令的 `--out` 是 `governance/review-reports/{loop}/{rN}-原生審查-sonnet.md`,`.unparsed.txt` 也落在旁邊。

- **規則內容**:`skills/lumos-code-loop/SKILL.md` 第 3 步、templates §0 要求所有席收齊前,先到的報告留在對話裡、不寫進硬碟,免得後到的席讀到先到那席的報告。
- **衝突**:這一席要跑約 2 分鐘再轉換,必然比其他席早或晚寫進 repo。同輪其他席還在跑時,報告已躺在 repo 內。
- **建議**:`--out` 改寫到 `$W`,收齊後再一次搬進卷證;`.unparsed.txt` 也一樣。

## F5 錨不到的發現不進帳,RETIRE-IF 的量測無從算起
severity: major
blocking: 是

引句:「它錨不到引句而被丟掉的發現超過三成」

file: `scripts/lumos:48645` 與 `scripts/lumos:10250`(`_report_reported_count`):

- **現象**:c4 的案例中,唯一一條發現引了 repo 外的路徑 `/etc/hosts:1`,被丟進「錨不到」段,席報告變成 `severity: clean`、`reported=0`。
- **後果**:帳上跟一席真的沒發現完全分不出來。
- **其他席的對照**:其他席錨不到的條目仍留著 severity 行,處置閘看得到,這一席卻悄悄蒸發。
- **量測落空**:RETIRE-IF 要量「錨不到而被丟掉的比例」,`gov --stats` 與 `canary record` 都沒有這個數字。
- **建議**:在報告末尾的錨不到段與總結句外,另在 `canary record` 的 note 或 intake 留一個機器可讀的條數;或對「全部錨不到」的報告給出明確警告,而不是安靜地變 clean。

## F6 無頭呼叫在對話裡跑會被 2 分鐘上限砍掉
severity: minor
blocking: 否

file: `skills/lumos-design-loop/templates.md:453`:指令是前景執行。spec 自己量到每次約 1.5–2 分鐘。專案 CLAUDE.md 與 `skills/lumos-code-loop/SKILL.md` 第 5 步(fix-check 條)都記載對話裡指令預設 2 分鐘上限,fix-check 因此要求在背景跑。§7.9 應照同樣寫法加 `run_in_background`。

## F7 引句只比對「patch 裡任一行」,沒綁定到該發現所在的檔案
severity: minor
blocking: 否

引句:「跟凍結 patch 裡某一行(去掉開頭的 `+`/`-`/空白與首尾空白)完全相同」

file: `scripts/lumos:48571`(`_seat_import_quote`):

- 比對用的是整份 patch 的行集合,不分檔案。複本的檔案若有一行恰好等於 patch 裡別檔的某行(例如 `return None`、`import os, sys`),就當引句通過。
- 被刪行為的發現,複本 HEAD 版沒有那一行,上下 3 行內就可能挑到無關的行當引句。
- `f["file"]` 沒限制在複本根底下,`Path(repo)/"/etc/hosts"` 這種絕對路徑或 `../` 都能讀到 repo 外的檔。
- 比對方式與 spec 寫的一致,但「引句全錨」的意義被稀釋。
- **建議**:引句限定來自 patch 裡同一個檔案,路徑用 `resolve()` 後必須落在 `--repo` 底下。

## F8 `@{upstream}...HEAD` 的三點 diff 可能與凍結 patch 的範圍不一致
severity: minor
blocking: 否

引句:「審的範圍是 `git diff @{upstream}...HEAD`,要先把被審分支的上游設成這輪的起點。」

三點 diff 取的是 merge-base 到頂端。若這一輪的起點不是頂端的祖先(例如分支中途合過主線),`/code-review` 審到的範圍會比凍結 patch 大。多出來的部分在轉換時被判錨不到,安靜丟棄(接 F5),而不是被標示為超出範圍。§7.9 應要求 `seat-base` 必須是頂端的祖先,不是就停下回報。

## F9 補等級那一步與暫存清理的缺口
severity: minor
blocking: 否

file: `skills/lumos-design-loop/templates.md:455-464`:

- **haiku 呼叫在哪跑沒寫**:若在 repo 工作目錄跑,會載入專案的 CLAUDE.md 與 hooks,並吃進被審 diff 的文字(`--json-schema` 的 enum 能限制輸出,但輸入面沒隔離)。
- **severity.json 沒存證**:`severity.json` 與 `raw.json` 在收貨後隨 `$W` 一起被刪,補等級是「審查員層宣告」,卻不在卷證裡,日後不能重現或稽核。
- **筆數不符無去向**:`severity.json` 條數不符時 rc2,但 §7.9 只寫「形狀認不得就改派同門通才」,沒寫筆數不符怎麼辦。
- **無頭呼叫的會談紀錄不歸清理規則管**:每次 `claude -p` 在 `~/.claude/projects/` 留下以暫存路徑命名的會談紀錄,內含完整 diff。全域暫存清理規則只管 `/tmp/lumos-seat-work`,這批殘留不在其中。

## F10 回退路徑對歷史帳安全,但會留下懸空的測試綁定
severity: minor
blocking: 否

引句:「編制改回同門通才:把 `_TIER_ROSTER` 鏡頭5 的備註還原,手冊那一節刪掉;轉換指令留著不影響其他流程。」

我查了 `_roster_family` 與 `_disposal_security_step`/`_auditor_matches_slot`。歷史帳裡的 `原生審查-sonnet` 只靠名字含 `sonnet` 判成同門,不依賴備註,不是資安席。所以舊迴圈回放不會出錯。但回退後 S4 的 `t_seat_import_roster_slot` 會對不上備註,計劃裡的 `[test:]` 綁定要一併撤掉,spec 沒寫。

blocking 的有 F1、F2、F3、F4、F5 五條,其餘 F6 到 F10 都是 minor;最高等級 major。
