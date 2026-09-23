severity: blocker

## F1 「code」前綴判準漏連字號,會誤擋真實存在的設計/審計迴圈(不是代碼審)

severity: blocker
blocking: yes

觀察到什麼:新擋的判準是 `str(loop).startswith("code")`——**沒有連字號**。但同一支 repo 裡早就有一個專門處理這個歧義的三值分類器 `_roster_kind`(`scripts/lumos:1528` 附近),它的 docstring 白紙黑字寫著:「code-(含連字號)=code;code 開頭無連字號=None(indeterminate,**歷史帳實有 code側刪除傳播守衛/codestage**)」。也就是說,repo 自己的治理帳裡真的存在名叫 `codestage` 的迴圈,九筆記錄橫跨 r1–r4(2026-07-18),**從頭到尾都沒有 report_path/snapshot_path/tier 欄位**,是道地的設計/審計迴圈(對應 `[[Projects/code階段強化_計劃]]`),不是代碼審。新擋的判準會把它一起收進「代碼審」。

怎麼重現:
1. 用臨時 vault 記一筆 `--loop codestage`(只帶 `--report`,不帶 `--snapshot`),得到:
   ```
   擋下:代碼審(codestage)的每一筆記帳都要帶 --snapshot——現在不擋的話,要到問處置閘才會發現,而那時帳本已經不能撤銷,只能整輪換編號重記
   exit: 2
   ```
   跟真代碼審 `code-對照` 印出來的訊息**一字不差**(只差迴圈名),而 `codestage` 歷史上從沒被要求過這件事。
2. 對照組 `--loop design-對照`(design 開頭)同樣缺 `--snapshot`,`exit: 0`,正常記進去——證明擋的正是「code 開頭無連字號」這個灰色地帶,而 repo 自己的分類器早就承認這個地帶不等於代碼審。

為什麼是 bug 而不是風格:這不是理論案例,是**這支同一份 repo 真實發生過的迴圈名**;修法自己的註解還寫「跟 doctor [I] 段與 code-loop 的既有判法同一個(code-<主題>)」,暗示會用連字號版本,但實際程式碼沒有連字號,跟它聲稱要對齊的 `_roster_kind`(用連字號分三值、且明文承認無連字號是不確定)以及同一函式往下 14 行、同樣在 `cmd_canary` 裡的另一道判準(`str(loop).startswith("code-")`,`scripts/lumos:7762`)都不一致。結果是:任何未來的設計/審計迴圈只要主題剛好用英文詞起頭恰好長得像 "code"(`codestage` 就是活生生的先例——主題「code 階段強化」),就會被強制套用代碼審才有的「第一筆就要 --report/--snapshot」規則,擋下合法寫入,且訊息還講成「代碼審」,誤導人去找一份根本不存在的凍結 patch。

引句:「if loop and str(loop).startswith("code") and not (report and snapshot):」
引句:「跟 doctor [I] 段與 code-loop 的既有判法同一個(code-<主題>)。」

查證:`scripts/lumos:1528`(`_roster_kind` 三值分類器,明文列出 codestage 為無連字號歷史案例)、`scripts/lumos:7762`(同一函式內另一處判準用 `code-` 含連字號)、`docs/.canary-log.jsonl`(grep `"loop": "codestage"` 有 9 筆,全部沒有 report_path/snapshot_path/tier 欄位)。


## F2 `--outcome` 結局帳(自主迴圈專用、結構上就不帶 report/snapshot)沒被排除,理論上會被新擋一起擋掉

severity: major
blocking: yes

觀察到什麼:`cmd_canary` 裡另有一條互斥規則(`scripts/lumos:7603-7606`):帶 `--outcome` 的「結局帳」跟 `--round/--severity/--report/--snapshot/--intake/--findings*` 這些審查席欄位互斥——真實的結局帳就是只帶 `loop+auditor+outcome`,**結構上永遠不會有 report/snapshot**。新擋的條件 `if loop and str(loop).startswith("code") and not (report and snapshot):` 完全沒有把 `outcome is not None` 排除在外,只要迴圈編號恰好以 "code" 開頭,結局帳就會被新擋攔下來。

怎麼重現:
```
lumos --vault <臨時vault> canary record none --loop code-auto-test --auditor orchestrator --outcome skipped
```
輸出:
```
擋下:代碼審(code-auto-test)的每一筆記帳都要帶 --report 與 --snapshot——…
exit: 2
```
把 `--loop code-auto-test` 換成不含 "code" 的 `--loop auto-test`,同樣的 `--outcome` 用法就 `exit: 0` 正常記進去。

為什麼是 bug 而不是風格:這不是「先強制、以後再放寬」的取捨,是這支程式**自己在前面 20 行內就定義**了「結局帳互斥於審查欄位」這個結構事實(`scripts/lumos:7598-7606` 的註解甚至直接寫「真實結局帳只帶 loop+auditor+outcome」),新擋卻沒有沿用這個已知事實去排除它。目前 `docs/.canary-log.jsonl` 裡的結局帳全部用 `auto-YYYY-MM-DD` 這種日期化編號(掃過全部帶 `outcome` 的紀錄,沒有一筆迴圈編號以 "code" 開頭),所以還沒真的炸過;但這只是命名巧合沒撞上,不是規則本身沒有這個洞——只要有一天自主迴圈的主題編號剛好起頭像 "code"(不受任何機制禁止),結局帳就會無聲被擋在外,而錯誤訊息還會講成要補一份根本不該存在的「凍結 patch」。

引句:「_miss = [f for f, v in (("--report", report), ("--snapshot", snapshot)) if not v]」

查證:`scripts/lumos:7598-7606`(結局帳與審查席欄位互斥的既有規則,結局帳只帶 loop+auditor+outcome)、`docs/.canary-log.jsonl`(`grep outcome` 掃過的既有結局帳全部是 `auto-*` 編號,零 "code" 開頭案例——目前只是還沒撞上)。


## F3 壓提交訊息把「git merge-base 判定失敗」的所有原因都講成「多半是壓過提交或 rebase」,對非該原因的情況會誤導

severity: major
blocking: yes

觀察到什麼:改動只把 `if anc.returncode != 0:` 這一分支的訊息換成「多半是壓過提交或 rebase 改寫過歷史」,但 `anc.returncode != 0` 涵蓋的不只是「邏輯上不是祖先」(`git merge-base --is-ancestor` 回傳 1),**也涵蓋 rec_sha 本身在目前這份 repo 裡根本找不到這個物件**(找不到會 `fatal: Not a valid commit name`,回傳 128)——這種情況常見於:留痕帳裡的 sha 被寫壞/打錯、repo 是淺 clone 缺物件、或該 commit 已被 gc 掉。這兩種截然不同的原因,現在會印出同一句「多半是壓過提交或 rebase」。

怎麼重現(直接呼叫改動後的函式,不需要真的壓過任何提交):
```python
ok, why = m._codeloop_record_valid(Path(d), "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef", head)
```
輸出:
```
ok= False
why= 記錄 sha deadbeef 不是目標 f95ee945 的祖先——多半是壓過提交或 rebase 改寫過歷史(內容沒變也一樣失效)。重來:表態 `lumos pitfalls --diff <範圍> --dispositions-template --carry` 再 `lumos code-loop dispositions <檔>`;審查留痕重跑 `lumos code-loop pass --note "…"`
```
這裡的 `rec_sha` 從頭到尾沒被壓過、也沒被 rebase 過——它根本就不是這個 repo 認得的物件,但訊息仍然斷言「多半是壓過提交或 rebase」,並且給出的重來指令(重跑表態、重跑 `code-loop pass`)對「留痕帳本身壞掉/sha 打錯」這種情況是文不對題的建議。

為什麼是 bug 而不是風格:呼叫路徑是真的可達的——`_codeloop_record_valid(repo_root, str(rec.get("head_sha") or ""), marker_sha)`(`scripts/lumos:28836`)讀的是**之前寫進治理帳的 sha**,不是當場算出來的,沒有任何前置檢查確認這個 sha 在目前 repo 裡還存在;一旦帳面壞損或跨環境(例如換了一份沒有該物件的 clone)去驗證,就會踩進這條路徑。這支修法原本要解決的問題正是「訊息看不出原因、人瞎猜」,但新訊息把「猜對一種原因」跟「講死只有這一種原因」混在一起,對非壓提交的情況反而比舊版「只丟兩個 sha」更誤導人(舊版至少不會給錯方向)。

引句:「return False, (f"記錄 sha {rec_sha[:8]} 不是目標 {marker_sha[:8]} 的祖先——多半是壓過提交或 rebase 改寫過歷史"」

查證:`scripts/lumos:28836`(`_codeloop_record_valid(repo_root, str(rec.get("head_sha") or ""), marker_sha)`,讀治理帳裡存的 sha,無前置存在性檢查)、實測 `git merge-base --is-ancestor <不存在的sha> <HEAD>` 回傳 128 並印 `fatal: Not a valid commit name`(非邏輯上的「不是祖先」)。


## 已驗過但沒發現問題的路徑(供對照)

- Lens ②(新擋與定錨後強制擋的順序/訊息打架):兩道擋都在 `cmd_canary` 內,新擋(`scripts/lumos:7713`)在定錨擋(`scripts/lumos:7722`)之前,條件是子集/超集關係——凡是新擋該擋的(code 開頭缺 report/snapshot),舊擋的條件必然同時成立,所以不會出現「兩道都該擋卻只印一道無關訊息」;唯一會被新擋「搶先攔截、蓋掉本來該走的規則」的情況正是 F1 那種被誤判成代碼審的設計迴圈——已併入 F1,不重複開一條。
- `caught`/`missed` 這兩種 kind 舊用法:已於 2026-08-14 植入協議停用,`skills/lumos-code-loop/reference.md:173` 明寫現行一律走 `canary record none … --report --snapshot`,沒有找到目前仍在用、且結構上豁免快照的 `caught`/`missed` 現行路徑。`code-loop pass/skip` 是完全獨立的 `cmd_code_loop`,不經過 `cmd_canary`,不受這次改動影響。
- Lens ④原句提到的「是祖先但中間動了程式」那個失效原因:程式碼路徑上完全沒動(`scripts/lumos:91` 那句 `f"記錄 sha {rec_sha[:8]} 之後動了代碼(非純簿記增量)"` 維持原樣,是另一個獨立分支),不會被印成「壓過提交」——這個子案例本身沒問題,但同一個分支底下有別的原因會被誤標(即 F3)。
