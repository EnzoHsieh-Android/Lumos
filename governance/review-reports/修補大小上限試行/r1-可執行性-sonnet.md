severity: major

以下是我在 `/tmp/lumos-seat-work/修補大小上限試行/可執行性-sonnet/repo` 造的小例子上實跑出來的結果。例子有三個提交:base、r1 凍結的 C1、r2 修補。r2 工作樹有 2 個已追蹤檔各加 2 行、1 個改名檔加 1 行、1 個二進位檔、1 個未追蹤新檔 10 行,另有卷證檔和 `docs/.canary-log.jsonl` 的改動。

**finding 1**
引句:「對工作樹的新增行數加總,不算」
severity: major
blocking: 是
- 照字面做,指令只有 `git diff --numstat <C1>`,沒有寫排除路徑要怎麼下。
- 我實測:未追蹤的新檔 `git diff --numstat` 完全不算。工作樹這樣數是 5,提交後同一份修補是 16。「新檔」正是新機制最常出現的形狀,所以最容易漏的就是最該被限制的部分。
- 二進位檔的新增欄是 `-`,直接加總會出錯或被當成 0。
- 預設會偵測改名,`old.txt => new.txt` 只算 1 行;`--no-renames` 算 2 行,第二人會得到不同的數。
- 排除路徑要用 `-- . ':!governance/review-reports' ':!governance/replay' ':!docs/.*-log.jsonl'`。我驗過 `':!docs/.*-log.jsonl'` 這種 fnmatch 寫法有效。文件沒給這串指令,兩個人各寫各的。
- 應該是:寫死一條指令。先 `git add -N` 或先 stage,加 `--no-renames`,帶排除 pathspec,加總時略過 `-`,並指定帶 `-c core.quotePath=false`。

**finding 2**
引句:「數出來的 + 行是同一個數」
severity: major
blocking: 是
- 我用 templates.md §3.1 的指令產生 `r2-repair.patch`,實際不是同一個數。
- 該指令的註明是「含兩版之間全部已提交變動」,且「不要按作者的修正紀錄挑檔」,所以不排除路徑。
- 同一份修補實測:patch 裡 `^+` 行有 65 條,其中 9 條是 `+++` 檔頭,其餘包含卷證檔內容。排除 `+++` 後是 56,仍遠大於 numstat 排除路徑後的 16(同為 `--no-renames`)。
- 照字面,有人拿 patch 的 `+` 行去驗收或回顧,會得到 4 倍的數。
- 應該是:刪掉「同一個數」這句,或改成「patch 須先濾掉排除路徑與 `+++` 檔頭才等於」。
- 另外,回放腳本算的是兩輪凍結 patch 的序列差(`difflib` 去重)。S6 寫「跟回放同一單位」,但實作是 numstat,兩者對搬移或重複行不一定相等,至少要註明是近似。

**finding 3**
引句:「當本試行第 3 至 5 案的某一輪修補寫好、準備提交時,編排者應先數這輪修補新增的行數」
severity: major ⚠
blocking: 是
- 「上一輪凍結時的提交」沒說從哪拿。SKILL.md 說派工單頂層加 `"base_commit"`,但 `code-repair-pilot-01/r2-dispatch.json` 的欄位裡就沒有 `base_commit`。其他迴圈的派工單也有缺的,例如 Codex 編排的幾份。
- 凍結快照是 `merge-base..HEAD` 的 diff,檔上沒有記 HEAD。
- SKILL.md 還允許「還沒推可以改寫那個提交」,即 amend 或壓成一個。我實測 amend 後舊 sha 在 `gc` 之後 `cat-file` 就找不到,記在 intake 的 sha 會失效。
- 應該是:規定凍結當下把 `git rev-parse HEAD` 寫進 `rN-dispatch.json`(或明寫「以 `r(N-1)-snapshot.patch` 反推」),並規定改寫提交後要更新這個值。

**finding 4**
引句:「對工作樹的新增行數加總,不算」
severity: major
blocking: 是
- 本分支歷史就有「Merge remote-tracking branch main」。如果兩輪之間把主線併進來,`git diff --numstat <C1>` 會把主線帶進來的變動全算進去。
- 我實測:併進 300 行的主線提交後,只加 1 行的修補數出 423(其中約 123 行是我造的 patch 與卷證)。
- 回放腳本是「快照對快照」,不受這影響,所以量到的單位和回放不同。
- 應該是:規定兩輪之間禁止 merge,或用 `git diff --numstat <C1> -- <本分支改動檔>`,或改用 `--first-parent` 的做法。

**finding 5**
引句:「仍超過就把不屬於任何 finding 的部分(新機制、格式、重構、附帶的改善)拆成另案或 Issue」
severity: major
blocking: 是
- 沒說哪些行屬於 finding。以下幾類無法由字面判定,兩個人會做出不同結果:
  - S2 要求壞例與好例的配對測試。
  - 專案鐵則 1、5 的 pre-commit 擋「改 code 沒動圖譜」,逼著同提交帶筆記行(docs/ 下的筆記不在排除清單,所以會被數進去)。
  - 為了 minor 寫的行數。
- 這些要不要數進 100,文件沒講:
  - 若數,編排者會被誘導少寫測試或筆記。
  - 若不數,又和「同單位」矛盾。
- 逼著拆成「另案」會和 pre-commit 衝突,測試和筆記不能獨立提交。
- 「分開記為了 minor 寫的行數」也沒有歸屬方法。同一個 hunk 同時修 major 與 minor 時,無法切分。
- 應該是:明列「測試、筆記、為 minor 寫的行各自算或不算」,並給歸屬規則。

**finding 6**
引句:「再不行才照常提交,並在未入帳 intake 寫明超過的行數與理由」
severity: minor
blocking: 否
- 修補發生時,上一輪 intake 通常已入帳。未入帳的是下一輪才會建的 `r(N+1)-intake`,而它在修補提交時可能還不存在。
- 如果這一輪是第三輪或達上限、不再有下一輪,就沒有可寫的 intake。
- 「每輪的修補新增行數與下一輪有沒有 major」記進逐案紀錄,但第 3 至 5 案的逐案紀錄只有計劃裡第 1 案的先例。欄位清單(行數、是否例外、為 minor 的行數、下一輪 major 有無)散在 S5、S6、分界三處,沒有一張欄位表。
- 末輪沒有「下一輪」時,該填未知還是不填,沒說。
- 順序也有循環:若先把行數寫進計劃再提交,而計劃本身在 docs/ 下,會被算進行數。
- 應該是:指定落點與寫入時機,並補欄位表。

**finding 7**
引句:「這是事後觀察,不是對照實驗;本節用剩下三案做前瞻試行」
severity: minor
blocking: 否
- 數字在不同處對不上。Systems 節點(`pitfalls-code-loop.md` 第 37 行)寫「187 個有 major 的續輪只有 7 輪因此變乾淨」。
- 驗證筆記與計劃寫「169 輪、16 輪」。
- 回放腳本的口徑會改變數字,兩份該以其中一份為準。這會讓下一個人重算時不知道要對哪個。
- file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:37`

**finding 8**
引句:「若三案的續輪下一輪有 major 的比例沒有低於回放全體續輪的 60%」
severity: major ⚠
blocking: 是
- 回放表格顯示,修補本來就在 100 行以下的 128 輪,下一輪有 major 的比例是 43%。所以即使完全沒有上限這個機制,小修補的輪次也自然低於 60%。
- 門檻設成 60% 幾乎必過,判不出上限本身有沒有用。
- 三案續輪極少,樣本不足。文件說「判不出就照實寫」是好的,但沒有給出可判的基準。
- 應該是:基準改用 43%(同量級修補自然率),或改比較有超過 100 行例外的輪與沒超過的輪。

固定席節點逐條判:
- 五篇 `Issues/探針*`:
  - 讀碼證據不足、Git 隔離缺口、共用沙盒清理失敗,三篇是 open。
  - 批次停止的剩餘工作那篇是 doing。
  - 健檢不可判資料那篇是 resolved。
  - 這五篇都是探針儀器的問題,跟 S6 的行數算法沒有直接衝突,我沒發現互相牴觸的條款。
- `Systems/pitfalls-code-loop`:
  - 其 WHY 行與 S6 方向一致。
  - 唯一的矛盾是 finding 7 的 187/7 與 169/16 數字。

總結:最嚴重等級 major,blocking 6 條(finding 1、2、3、4、5、8),minor 2 條(finding 6、7)。
