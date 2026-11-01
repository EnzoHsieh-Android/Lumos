severity: major

## 核對結果(正常路徑,修後 d5e8f27 仍成立)

- 帳只追加:相對 3383ff2,`git diff --numstat` 三本帳刪除欄都是 0(canary 13/0、governance 10/0、kill 1/0)。
- 撤回輪次:四個 token(CANARY-50e54023、CANARY-0d2cb76d、CANARY-702cedf0、CANARY-df2768c0)在 d5e8f27 的 `docs/.canary-log.jsonl` 都是 0 筆。nodes 為不帶 -std 的 converged 行是 0 筆。
- 帳內路徑:新增帳行的 `report_path`、`spec_path`、`snapshot_path`、`intake_path` 全部存在。帳行裡的 `plan` 與 `node` 是相對 `docs/lumos-toolchain-knowledge/` 的寫法,該目錄下檔案存在。
- 指紋:自己算了 sha256。`manifest.json` 列 20 檔,目錄實有 21 檔(多的是 manifest 自己),20 檔全部一致,沒有漏列或多列。
- 數字:
  - 本機測試 80 支;壞測試 7 支,其中 1 支(b2)本來就紅;既有測試 820。
  - 平板套件前後都是 488,`identical: true`。
  - 平板儀器測試:14 支加 1 支範本測試(套件名寫死,`.dev` 變體必紅)。
  - 七個錯的翻紅支數與收據目標數(16/16、2/2、9/1、7/5、5/5、4/2、3/3)跟 `fault-matrix-agent-tests.json` 與 `fault-checks/M*.json` 逐條對得上。
  - 壞測試:b1、b3、b6、b9 為 survived(rc=2),b7 為 detected(rc=0),b2 與 b4 沒有配對。
  - `controls.json` 六筆裝置歸因樣本,我拿 `scripts/test_quality.py` 的 `assertion_failure` 實跑,結果 4 筆認、2 筆不認,跟註記一致。
- 檔名:公開目錄 21 檔全是純 ASCII。修前版本(c08dc36)的 `fault-checks/` 和 `bad-test-checks/` 底下還有中文檔名,修後已改掉。
- 上輪三個問題:
  - 歸因樣本已加註「修補前量的」。
  - 帳句缺字已在驗證紀錄註明。
  - 設計審原編號的證據檔已自 d5e8f27 的樹移除(但見 finding 1)。

## Findings

### 1. 已撤回的設計審證據仍整段嵌在提交進公開 repo 的 r1-snapshot.patch 裡,真實識別字沒清掉
- 位置:`governance/review-reports/code-收證認得Truth與裝置字串比較/r1-snapshot.patch`,在 d5e8f27 的樹裡。這支檔是上一輪代碼審的差異材料,把原編號設計審的 `r1-snapshot.md`、`r1-整合-sonnet.md`、`r1-邊界-sonnet.md` 等當新增檔嵌了進去。
- 外流的類別(不貼原文),都在那支 patch 的行號裡:
  - 真實套件名片段:第 1739、2143 行。
  - 真實 ViewModel 類別名:第 1695 行。
  - 以這個類別名為前綴的測試類別名:第 1846 行。
  - 真實資料來源/欄位類別名片段與方法名:第 1651、1768、1781、1822 行。
  - 考場本機工作樹絕對路徑:第 1708、1785、1801 行。
- 同一支 patch 和 `r1-snapshot-B.patch` 也還帶著被撤回的四個 CANARY token,這是設計審那輪被撤的帳行。
- 驗證紀錄寫「公開 repo 不留」,README 寫不放考場原始碼,這兩句與事實不符。
- 當場重現(命令只用泛型規則,輸出只列行號):
  ```
  git -C /Users/enzo/harness/lumos-unit-test-drill show d5e8f27b334887c1c66763c3a1ab778e2a7e3f90:"governance/review-reports/code-收證認得Truth與裝置字串比較/r1-snapshot.patch" | grep -nE 'Category[A-Za-z]*ViewModel|com\.[a-z]+\.[a-z]+\.dev|/Users/enzo/mOrangePos' | cut -d: -f1 | tr '\n' ' '
  ```
  輸出:`1695 1708 1739 1785 1801`。
- 範圍:
  - `r1-snapshot-A.patch`、`r1-snapshot-B.patch` 用同一個規則是 0 筆(B 只帶撤回的 token)。
  - 整個 d5e8f27 的 `governance`、`docs` 底下,真實 ViewModel 類別名只出現在這一支檔。
- 前瞻風險:尚未提交的 `r2-repair.patch`(10 行命中)和 `r2-snapshot.patch`(5 行命中)同樣含有這些字串。若照 r1 的做法提交,會再公開一次,提交前要先清或改用去識別化的版本。
- 修前修後:
  - 修前(c08dc36):原編號 `Android單元測試標準實機演練/r1-snapshot.md` 直接在樹裡,同一規則命中 3 行,另有 4 個檔含真實識別字。
  - 修後:這 4 個檔已從樹移除,但同樣內容經由 `r1-snapshot.patch` 留在樹裡。
  - 修前查證:`git show c08dc36fe239076e40d54e3a903055389d18f245:"governance/review-reports/Android單元測試標準實機演練/r1-snapshot.md" | grep -cE '<同上規則>'`,輸出 3。
- 歸因:有證據的原有漏查。識別字在修前就在樹裡,修補只移除了原檔,沒處理它的嵌入副本。`r1-snapshot.patch` 這個載體是修後才進樹的新檔。
- 引句:「"spec_path": "governance/review-reports/code-收證認得Truth與裝置字串比較/r1-snapshot.patch"」
- blocking: 是
severity: major

### 2. README 新增的「子套件路徑一律攤平到 com.example.pos」跟同目錄內容矛盾
- `requirements.md` 寫著 `com.example.pos.category`。
- `fault-checks/M1.json` 到 `M7.json` 的 targets 也是 `com.example.pos.category.*`。
- `bad-tests.kt.txt` 與 `controls.json` 用的是 `com.example.pos.drill.*`。
- 讀的人會以為公開檔裡沒有任何子套件,實際上有 `category`、`drill` 兩層。這兩層是代稱或演練新增,不是識別字外流,但句子錯了。
- 修前修後:
  - 修前 README 沒有這句,檔案內容相同。
  - 修後 README 新增這句,內容沒動。
  - 查證:`git show <版本>:governance/eval/results/android-unit-standard-drill-20261101/README.md | grep -c '攤平'`,修前 0、修後 1。
  - 內容查證:`git show <版本>:.../requirements.md | grep -c 'com.example.pos.category'`,兩版都是 1。
- 歸因:有證據的修復回歸(修補新寫了一句跟內容不符的話)。
- 引句:「子套件路徑一律攤平到 `com.example.pos`」
- blocking: 否
severity: minor

### 3. README 說路徑已換成三種佔位符,但公開目錄裡一個佔位符都沒出現
- README 宣稱路徑換成 `<考場>`、`<會談暫存區>`、`<工具鏈工作樹>`。
- 目錄內 21 檔除了 README 自己,沒有任何一處用這三種佔位符,因為檔裡根本沒有路徑。
- 結果是句子描述了不存在的處理,誤導程度低。
- 查證:`grep -rln '<考場>\|<會談暫存區>\|<工具鏈工作樹>' <目錄>`,修前修後都只命中 README。
- 歸因:有證據的原有漏查。這句在修前 README 就有。
- 引句:「路徑換成 `<考場>`、`<會談暫存區>`、`<工具鏈工作樹>`」
- blocking: 否
severity: minor

### 4. 新增帳行記錄的提交不在 HEAD 的歷史上
- fix-check 兩行的 `head_sha` 是 `3bf6f792…` 和 `c06a57ca…`,converged 行的 commit 是 `d8d32a978`,kill-log 新增行的 commit 是 `c06a57caa`。
- 這幾個提交都能 `git cat-file` 取到,但都不是 HEAD 的祖先。它們靠 reflog 與未回收的物件庫存活,一旦 gc 回收,帳上的指紋就指不到東西。
- 修前版本 c08dc36 也不是祖先,binding 已承認「未被回收前」可取回。
- 查證:`for c in d8d32a978 3bf6f79 c06a57c c08dc36; do git merge-base --is-ancestor $c HEAD && echo yes || echo no; done`,四個都輸出 `no`。修前同樣是這個結果。
- 歸因:未判定。這是修補期間重建提交造成的,不能說是哪次修補獨有。
- 引句:「"head_sha": "c06a57caacf261ad8966cb806f076afb01ac1781"」
- blocking: 否
severity: minor

### 5. 新增規格閘帳行 SPEC-b1f71bc4 記錄的測試名在 repo 裡找不到
- 該帳行 `tests` 列了 `t_test_quality_cli_drill_cases_present`。
- 這個名字在 `scripts/test_lumos.py` 與整個 repo 都沒有定義。
- 後一行 SPEC-d6bca914 列的是 `t_drill_quality_cli_cases_present`,該函式存在(1 個定義)。看起來是改名,帳只能追加,沒說明。
- 影響:想重放 SPEC-b1f71bc4 的人會找不到那支測試。
- 查證:`grep -n "def t_test_quality_cli_drill_cases_present" scripts/test_lumos.py`,0 筆。
- 修前版本帳裡沒有 SPEC-b1f71bc4,這行是修補期間新增的。
- 歸因:未判定。
- 引句:「"tests": ["t_secev_drill_s5_truth_fault_counts_like_assertion", "t_secev_drill_s5_truth_junit_declared_is_assertion_failed", "t_test_quality_cli", "t_test_quality_cli_drill_cases_present"」
- blocking: 否
severity: minor

### 6. 新增的審查報告內有使用者名與本機絕對路徑
- 兩處都是工具鏈自己的路徑,不是考場:
  - `code-收證認得Truth與裝置字串比較/r1-卷證-sonnet.md` 第 28 行,是公開 repo 的本機路徑。
  - `Android單元測試標準實機演練-std/r1-架構對齊-sonnet.md` 第 19 行,是另一個本機實驗目錄路徑。
- 都帶使用者名 `enzo`。repo 其他舊檔本來就有同類路徑(例如 `docs/.canary-log.jsonl` 第 439 行),所以這次不是新型態,只是這批新增檔又帶進去。
- 查證:`git grep -n '/Users/enzo' d5e8f27b334887c1c66763c3a1ab778e2a7e3f90 -- 'governance/review-reports/code-收證認得Truth與裝置字串比較/r1-卷證-sonnet.md' 'governance/review-reports/Android單元測試標準實機演練-std/r1-架構對齊-sonnet.md'`。
- 歸因:有證據的原有漏查(舊檔早有同類)。
- 引句:「"report_path": "governance/review-reports/code-收證認得Truth與裝置字串比較/r1-卷證-sonnet.md"」
- blocking: 否
severity: minor

總結:最嚴重等級 major,blocking 1 條
