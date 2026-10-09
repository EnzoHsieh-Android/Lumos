severity: major

審查範圍:逐節讀完 `/tmp/舊句兩道轉擋-r2.md`,交叉引用全數存在。我核對了 6 個函式與常數名、10 個既有測試名、6 篇 `[[...]]` 節點和手冊子檔;`t_old_sentence_default_follows_gate`、`t_reread_block_layer1` 現在是 0 個,屬待新增的新測試。我用 `git clone` 把 repo 複製到 `/tmp/lumos-seat-work/舊句兩道轉擋/併發2-sonnet/clone` 實測,另在 `.../sim` 建了一個極簡 git repo,沒有動審查對象的 repo。派工尾端沒有附固定席節點,所以沒有節點要判。

## Finding 1:ack 對「一字不差的原文」,本機增量範圍和 CI 累計範圍的候選不同,CI 會在主線確定變紅,PR 階段看不到

severity: major
blocking: 是
判準:這和 spec 自己拿來拒絕 CI 第一層的理由一樣,都是主線留下紅燈;不改設計不該進實作。

- spec 段落:〈重讀:候選與兩層〉第二層、〈照留表態〉、〈掛鉤與 CI〉。
- 兩層都只對「候選」(範圍內程式和管它的筆記都改了)才跑。本機推送的範圍是遠端舊值到頂端的增量,CI 在主線推送時用 `BEFORE..SHA` 的累計範圍。
- 時序 A(PR 分兩次推):
  1. 第一次推送改程式和筆記 N,判定紀錄點出規則類行 L,作者表態並提交。
  2. 第二次推送只改 N 裡的 L(例如把 `[confirmed:]` 日期往後改),沒動程式。
  3. 本機第二次推送沒有候選,放行。
  4. 合併後 CI 累計範圍裡 N 是候選。引句還在 L',但表態記的是舊的 L,所以第二層擋,CI 紅,主線上只能補一筆表態。
- 實驗(`clone`,在 `scripts/lumos` 和 `check-t-sentinel.md` 各改一次,c1 改程式加筆記、c2 只改筆記):

```
--- local 2nd push (old=C1) ---
回頭重讀提醒:這次沒有要對照的家筆記
--- CI on main after merge (before=B) ---
回頭重讀提醒:這次改到的程式,有 1 篇守檔筆記這次也改了、還沒對照過這一版程式(已對照 0 篇)
```

- 時序 B(分支基底過舊):
  1. PR1 帶著判定紀錄、表態、程式一起合進主線。
  2. 基底過舊的 PR2 在樹裡沒有那份紀錄,它把 L 的日期改掉,另外改了程式。
  3. PR2 的本機推送放行。
  4. 合併後主線樹同時有 PR1 的紀錄與表態、PR2 的新 L'。
- 實驗(`sim`,`git merge` 自動合併成功,沒有衝突):

```
quote still in merged line: True
ack text == merged line: False
```

- 為什麼修不掉:CI 的 reread 步驟只在 `push` 到 main 時跑。依據是 file: `.github/workflows/ci.yml:253` 的 `if: github.event_name == 'push'`,和 `ci.yml:4-7` 的 `on: push: branches: [main]` 加 `pull_request`。所以第一次看到這個紅燈就是合併之後。
- 表態比對的鍵是路徑加去頭尾空白的整行,依據是 file: `scripts/lumos:37237`(`_drift_ack_key`);RULE 行的 `[confirmed:]` 日期是最常被改動的欄位。

引句:「沒有對到「同一路徑、同一行原文、綁了點出它的那份判定紀錄對照指紋」的 kind=reread 表態」
引句:「合併讓程式 blob 變了,指紋必然對不上,擋了只會在主線留下修不掉的紅燈」

建議:ack 的鍵改成不含 `[confirmed:]` 等日期欄位的穩定形,或讓 CI 第二層對「表態文字不符但引句仍在」只印不擋。

## Finding 2:第一層用 `CI` 環境變數當開關,本機可以無痕繞過第一層

severity: major
blocking: 否
判準:繞過第一層不需要任何旗標,而且帳上沒有 `skipped-env` 事件;可以修,但不影響其他設計。

- spec 段落:〈重讀:候選與兩層〉第一層、S5、RETIRE-IF。
- 現有程式用 `src = "ci" if os.environ.get("CI") else "hook"`,依據是 file: `scripts/lumos:34980`。字串 `0` 或 `false` 也算「有值」,我在 python 裡驗過(`'0' True`、`'false' True`、`''` 為 False)。
- 時序:本機執行 `CI=false git push`,hook 把環境變數繼承給 `lumos`,第一層只印不擋。
- 這樣不會記 `skipped-env`。spec 的 RETIRE-IF 第二條只看 `LUMOS_SKIP_REREAD_CHECK` 的 `skipped-env`,看不到這條繞路。
- 反過來,任何開發機或代理程式環境有設 `CI`,就整台機器悄悄少一層。我在這個會談的環境裡查過,`CI` 沒有設。
- 測試端沒問題:`_rr` helper 已經在 file: `scripts/test_lumos.py:63678` 清掉 `CI`。

引句:「有值時第一層只印、不擋——CI 在主線推送時用整個 PR 的累計範圍重算」

建議:改由 ci.yml 明確傳旗標(例如 `--ci`),不用環境變數推斷;至少改認 `GITHUB_ACTIONS == "true"`,並把這條路徑記成事件。

## Finding 3:第一層在 PR 流程裡實際上哪裡都不強制,「兩層都擋」說得過頭

severity: major
blocking: 否
判準:spec 已承認「只在本機推送前擋」,但沒承認拆次推送會整個漏掉;屬於範圍表述與可補強的缺口。

- spec 段落:〈原問題與範圍〉、第一層、〈對消費專案的影響〉。
- 時序:
  1. 第一次推送只改程式 C,沒有 N,不是候選。
  2. 第二次推送只改 N,沒有 C,也不是候選。
  3. 合併後 CI 累計範圍裡 N 是候選,但第一層在 CI 只印、不擋。
  4. 第二層只在已有判定紀錄時才有東西可判。判定者從沒被叫起來,所以沒有紀錄,CI 綠。
- 實驗同 Finding 1 的 A(本機「沒有要對照的家筆記」,CI 列出候選)。
- 任何用 `git push --no-verify`、或在沒有 hook 的機器上做的 PR,第一層同樣永遠不會被看見。這正是 `ci.yml` 開頭註解說的「CI 是後盾」想擋的情形。
- 補強:CI 上可以不比對指紋,只問「這篇候選依路徑有沒有任何已提交紀錄」。這不受合併造成的 blob 漂移影響,spec 的「必然對不上」只在主線同時動過同一支程式時才成立。

引句:「候選照舊(推送範圍裡程式和管它的筆記都改了的守檔筆記),範圍照舊。」
引句:「同一個 PR 先推改程式與筆記、再推只改程式 → 合併進主線後 CI 第一層不擋(只印),第二層照依路徑找到的紀錄判」

## Finding 4:`drift ack --kind reread` 說「加進 `_DRIFT_BOUND_KINDS` 的比對」,照字面做會讓指令壞掉;`_DRIFT_KINDS` 沒列進清單

severity: minor
blocking: 否
判準:S17/S18 的測試會抓到,屬於實作時的規格矛盾,不是上線後的洞。

- spec 段落:〈照留表態〉。
- `_DRIFT_BOUND_KINDS` 在三個地方被用到:
  1. `cmd_drift_ack` 對這類種類會呼叫 `_drift_current_finding`,依據是 file: `scripts/lumos:37500`。reread 不是狀態發現,會得到「現在不是 reread」,回 2。
  2. `_drift_ack_buckets` 只收有 `related` 和合法 `seq` 的表態,依據是 file: `scripts/lumos:37283`。
  3. `_drift_bound_latest` 只取 seq 最大的那幾筆,依據是 file: `scripts/lumos:37321`。
- 最後一項尤其會誤擋:較早的 ack 綁 `verdicts=[X]`,另一個工作樹較晚的 ack 綁 `[Y]`,合併後 X 那一列變成沒涵蓋。第二層需要的是聯集語意。
- spec 只提到 `_DRIFT_KIND_NAMES`,沒列 `_DRIFT_KINDS`。但它被三處使用:file: `scripts/lumos:37232`(`_drift_load_acks` 過濾)、`:37411`(`--kind` 檢查)、`:50311`(argparse choices)。`_DRIFT_SCAN_KINDS` 也從它推導,依據是 file: `scripts/lumos:35025`。〈回退〉那段其實預設 `_DRIFT_KINDS` 含 reread,設計段卻沒寫。

引句:「reread 加進 `_DRIFT_BOUND_KINDS` 那一類的比對」
引句:「第二層只認 `verdicts` 含點出那一列的紀錄指紋的表態」

建議:reread 另走自己的分支(像 m1 的 `_drift_m1_split_acked`),`verdicts` 取聯集,並明列 `_DRIFT_KINDS` 與 argparse choices 要改。

## Finding 5:第二層以判定者的 `quote` 為準;`quote` 不保證逐字出自筆記,對不上就靜默放行,太短則過度比對

severity: minor
blocking: 否
判準:實測 6 筆全部逐字,所以頻率低;但失敗方向是靜默放行,補一個後備很便宜。

- spec 段落:〈重讀:候選與兩層〉第二層第一、二點。
- 派工詞只要求「原句(節錄即可)」,依據是 file: `scripts/templates/note-audit-reread.md:14`。`_note_reread_rows` 不檢查 `quote` 是不是 `text` 的子字串,`text` 才是工具從筆記取來的準值,依據是 file: `scripts/lumos:34508-34535` 與 `cmd_note_audit_reread_record` 設 `r["text"]` 那行。
- 時序:判定者回報「…節錄…」或換了全形標點,頂端版筆記全文找不到引句,spec 就判「這一列算處理過」,即使那一行完全沒動、仍是規則類行。
- 實測:對現有 5 份紀錄的 6 列算 `quote in text`,6/6 為真,所以目前沒有實例。
- 反方向:同一份紀錄裡 `quote` 只有 18 到 62 字。若判定者給很短的詞,「含這段引句的每一行」會把其他從沒被判過的規則類行也算進去,而且歷史紀錄不會過期。另外,實測 6 列的 `row.line` 和現在筆記的實體行號已經對不上(47 對 57、35 對 46),所以不能用行號,這點 spec 選對了。

引句:「頂端版筆記全文找不到這段引句 → 這一列算處理過(改掉或刪掉了)。」
引句:「找得到 → 看含這段引句的每一行是不是」

建議:`reread-record` 收件時驗 `quote` 是 `text` 的子字串,否則以 `text` 取代;第二層比對 `quote` 失敗時退回 `text`,而不是算處理過。

## Finding 6:判不了改擋後的資源與全域性問題

severity: minor
blocking: 否
判準:都是邊界,有出口(刪檔、重跑),沒有確定性紅燈。

- spec 段落:〈判定紀錄檔用…讀〉、〈回傳碼與判不了〉、〈實務隱患〉第三點。
- 讀哪些檔:spec 寫「下所有判定紀錄」,沒說只收檔名合 `_NOTE_REREAD_VERDICT_NAME_RE` 的。`.gitkeep`、`.tmp-wlf` 殘檔都會「讀不成 JSON」,變成每次推送(含 CI)對任何候選都判不了。但只有「有候選」的推送才會碰到,純修檔的推送會提早回傳,所以出得來。`.tmp-wlf` 沒被 `.gitignore` 擋,工具印出的 `git add governance/reread-verdicts` 會一併加進去。
- 總量超過 8 MB 時,`_nodehome_cat_blobs_capped` 是逐檔略過、回 None,依據是 file: `scripts/lumos:29495-29524`。spec 要「印是哪個檔」,但總量超限時指不出單一檔,也沒有清理計畫。紀錄只增不減。
- 時限:`_nodehome_cat_blobs_capped` 預設 `timeout=60`,spec 沒說要不要傳 `deadline`,依據是 file: `scripts/lumos:29495`。`_note_audit_resolve` 與 `_push_range_start` 內的 git 呼叫各自 20 秒上限(file: `scripts/lumos:44818`),也不歸 `_NOTE_REREAD_BUDGET_SEC=30`(file: `scripts/lumos:34326`)管。所以「約 30 秒」不保證,一次 `_lens_git` 超時(回 None)就會變成 rc 1。
- 實測耗時:這個 repo 用 `0000..HEAD` 搭配 `origin/main` 退 600 提交,37 篇候選共 4.8 秒;小範圍 1.2 秒。CI 機器較慢時的真實值沒有量過。
- 「現在 5 份約 20 KB」不準:`ls -la` 實際合計 7,855 位元組(2765+2336+450+1847+457),方向安全,但算不準。

引句:「判定紀錄檔用 `_nodehome_cat_blobs_capped` 讀,單檔上限 256 KB、全部上限 8 MB」
引句:「讀頂端提交裡 `governance/reread-verdicts/` 下所有判定紀錄」
引句:「現在 5 份約 20 KB」

建議:明寫只讀檔名合正規式的檔,把 `deadline` 傳進去,總量超限時印出最大的幾份檔名。

## Finding 7:RETIRE-IF 靠的治理帳在 CI 與擋下之後寫不回主線

severity: minor
blocking: 否
判準:只影響上線後的量測,不影響擋放行。

- spec 段落:〈原問題與範圍〉的帳數字、RETIRE-IF。
- 帳檔 `docs/.governance-log.jsonl` 是被追蹤的檔,hook 擋下時的 `blocked` 事件寫在工作目錄,要等下一次提交才會進主線。
- CI 在 runner 上寫的事件永遠不會被提交。RETIRE-IF 想量「CI 的 blocked」是量不到的。
- 我另外核對了 spec 引用的舊數字,主線帳確實是 `reminded` 18、`recorded` 5、`none` 12,舊句檢查 35 次全部 `passed`,數字正確。

引句:「上線前已提交的 5 份紀錄裡點出的規則類行,上線那次推送就要處理一次」

這句順手查證:現有 6 列裡目前在筆記裡找得到引句的只有 2 列,都不是規則類行(一列在正文,一列是沒帶 `[test:` 的 `WHY:`),所以上線第一次推送不會被這 5 份舊紀錄擋。

## 各節結論

- 〈原問題與範圍〉:數字已查證,另見 Finding 3。
- 〈設計〉的開關:已讀,無 finding。我只讀了 `_drift_retire_config` 與 `_drift_old_sentence_config`,都在,先例可套;warn 與 off 的邊界沒有深入驗。
- 〈回傳碼與判不了〉:`_note_audit_resolve` 的 `reasons` 目前只有重讀兩處在傳,spec 的說法屬實,依據是 file: `scripts/lumos:34752`、`:34949`。其他見 Finding 6。
- 〈輸出〉:已讀,無 finding。字串過 `_note_reread_show` 與 `shlex.quote` 的要求完整。
- 〈掛鉤與 CI〉:整個 CI 步驟只在 main 推送時跑,見 Finding 1。
- 〈要一起改的說法〉與〈回退〉:已讀,無獨立 finding。〈回退〉依賴 `_DRIFT_KINDS` 含 reread,見 Finding 4。
- 〈對消費專案的影響〉:補充一條,沒有獨立編號。消費專案若照手冊在自己的 CI 用預設淺層 clone,新程式的淺層 clone 判斷(S15)會回 0,等於 CI 悄悄不跑。手冊(`skills/lumos-project-notes/commands/06-代碼審與推送.md` 約 96 行)應補上 `fetch-depth: 0`。
- 〈驗收條款〉:S1 到 S21 已讀,無獨立 finding,缺口併入前面各條。

## 實務隱患鏡頭

- 金流:無。只動本機與 CI 的檢查回傳碼。
- 不可逆:無。擋下可用 `LUMOS_SKIP_REREAD_CHECK`、改設定或補提交恢復;Finding 1 的紅燈也用補一筆表態的提交修好。
- 對外送出:無新增。判定紀錄把筆記原句(單句最多 500 字)寫進 `governance/`,和筆記同庫同可見度。
- 守衛面:有,即 Finding 1 到 3。
- 併發:有。除 Finding 1,工具印出的 `git add governance/reread-verdicts && git commit` 會把共用工作目錄裡別的會談的紀錄一併加進去。使用者的全域規則要求「只加自己的檔」,所以這句提示應改成列具體檔名。
- 資安(字串跳脫):無。路徑和引句已列入 `_note_reread_show`,節點名用 `shlex.quote`。
- 資源與效能:見 Finding 6。
- 相容(消費專案):有,見上面的補充。

最嚴重的是 Finding 1(表態對整行原文、本機增量與 CI 累計候選不同,導致主線 CI 確定變紅且 PR 階段看不到);共 7 條 finding,blocking 共 1 條。
