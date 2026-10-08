severity: minor

# 殺傷力配方當場試跑 代碼審(另開一輪)第 2 輪 通才-opus 席報告

臨時目錄:`trc-r5-work-通才-opus/`。`repo` 是 40293f99(被審版本),`repo-base` 是 573d911e(這段修正之前,當對照組)。先核對過:凍結 patch 的程式與測試部分,跟 `git diff 573d911e..40293f99 -- scripts/` 逐行相同(去掉 index 行後 md5 一致)。

用到的腳本:
- `grid.py`:上一席的網格腳本,原樣複製。在兩個 clone 各跑一次,每次 1136 格,每格一個獨立 repo、真跑 `scripts/lumos guard kill`。
- `cmp.py`:逐格比較兩次網格的結果。
- `judge_diff.py`:把新舊兩版的 `_kill_recipe_judge` 對 22684 條配方逐一比較。
- `repro_json.py`:F1 的最小重現。

## 五項驗收(白話)

| 項 | 判定 | 依據 |
|---|---|---|
| ① 判法與原地擋共用 `_kill_old_bad`/`_kill_new_bad` | **修好了** | 判法本身沒變:22684 條配方(file 12 種寫法 × old 9 × new 7 × test 6 × platform 5,外加 4 種不是物件的元素),新舊兩版回傳的 dict 逐字相同,差異 0 筆。doctor P2 和 kill-add 提醒都吃這支,所以它們的判定也不變。guard kill 這邊,old/new 的各種形狀在正式、`./`、連結、大小寫四種 file 寫法下,不論帶不帶 `--id`、帶不帶合約片段、人讀或 `--json`,沒有一格當掉。上一輪 F1 的兩種(沒寫 old 加空檔、new 帶替身字元)從 `1💥` 變成回 2、判 error「配方欄位格式不對」。 |
| ② covers 不是清單、多寫的 detail 不是字串 | **修好了** | `covers=5`、`covers=true`、`detail=5` 三種共 88 格,從 `1💥` 變成照跑。好配方是回 1(killed_unattributed,測試環境整套一起跑),大小寫寫法是回 2(revert 失敗,這是既有行為)。 |
| ③ 合約片段過濾改回 `in` 比對,只在丟例外時不算 | **修好了** | invariant 是清單或物件、帶片段時,恢復成修正前的照跑(各 16 格,回 2 變回 1)。數字和 null 丟 TypeError,判成「沒有任何突變配方可跑」回 2,不當掉。物件型 invariant 比的是鍵、要整個相等,清單比的是成員,跟改動前的行為一致,註解寫的「行為不變」屬實。元素不是物件時 `r.get` 會丟 AttributeError、沒被接住,但這是既有行為:不帶 `--id` 本來就崩,Issue 也有列;帶 `--id` 時挑配方會先擋下。 |
| ④ 挑配方的判法兜底改成印一行 | **修好了** | `⑥g` 實跑綠。印在標準錯誤、有「⚠ 提醒:」前綴、例外訊息經過 `_kill_esc`,所以 `--json` 的標準輸出不受影響。 |
| ⑤ `--json` 把落單替身字元改寫成 JSON 跳脫 | **修了但漏同類**(F1) | 只有替身字元出現在不寫進 kill-log 的欄位(old、detail、attr_excerpt)時才修好。出現在 invariant、test、platform、note、covers、tail 時,程式在前一步寫 kill-log 就當掉,改寫那一行根本跑不到。Issue 把這幾種寫成「只有人讀輸出會崩」,跟實測不符。 |

## 回歸檢查

- **改動前後判法結果:** 22684 條配方逐一比對,完全相同(見 ①)。
- **網格新舊對照:** 1136 格中有變動的格子都在預期內,全部是「當掉回 1 → 擋下回 2 或照跑」,或「片段過濾恢復照跑」。其餘只是 error 說明的字面變了:old 和 new 的原地擋改用共用函式的長說明,對照測試用「配方欄位格式不對」比對,不受影響。沒有任何一格從不當掉變成當掉,也沒有回傳碼變得更寬鬆。
- **`--json` 是否仍是合法 JSON、一般中文是否照舊不跳脫:** 沒當掉的格子,`--json` 一律恰好一行合法 JSON(1136 格裡,不當掉、不是早退擋下、卻不是一行 JSON 的格子是 0)。重現腳本也確認:好配方的輸出直接含「上限恆為5」原字,沒有被跳脫;old 帶替身字元時輸出 `\ud800`,`json.loads` 讀得回來。
- **不帶 `--id` 的回傳碼與 `--json` 純度合約:** guard-kill 的兩條合約都守住。「rc 優先序」:新的 error 都回 2,survived 仍回 1。「`--json` 成功跑完時恰一行」:沒當掉的格子全部符合。仍然當掉的格子(見下)都回 1、標準輸出是空的,這些是 Issue 裡已列的既有問題,不重報。
- **新版仍會當掉的形狀(網格):** 元素不是物件、file 是數字/null/清單/含 NUL、platform 是清單或物件(這幾種只在不帶 `--id` 時當掉);test 帶替身字元(只在不帶 `--id` 時);invariant、file、platform 帶替身字元(帶不帶 `--id` 都當掉,而且**人讀和 `--json` 都當掉**)。
- **跑過的測試(在自己的 clone):** `guard_kill_only_ids` 27、`kill_recipe_check_matches_guard_kill` 92、`guard_kill_json_purity` 6、`guard_kill_rc_precedence` 4、`doctor_kill_recipe_drift` 30、`guard_kill_add_warns_drifted_recipe` 31、`doctor_p2_lists_survived` 13、`guard_kill_add_try` 7,全部通過,0 失敗。
- **固定席(`lumos impact --diff 573d911e..40293f99`):**
  - 直接相關的是 Systems/guard-kill 的兩條合約,上面已逐格核對。
  - Issues/guard kill遇到格式壞的配方整支崩潰:清單有誤,見 F1。
  - Projects/殺傷力配方當場試跑_計劃:〈實作紀錄〉有同一句「改寫成 JSON 跳脫」,但沒寫出只修了部分欄位,見 F1。
  - 其餘固定席(bound-tests-gate、授權與歸屬、測試假綠形態、lumos-cli-read/lifecycle、design-loop、pitfalls-code-loop、loop-convergence-recording、reversibility-governance-ledger、check-t-sentinel、check-r-guard、節點範圍與索引守衛、lumos-deinit、cochange-guard、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim 三支、規格落成、雙向門、逃逸自動記、core-invariant-baseline、judge-severity-gate):這段修正只動到 guard kill 與殺傷力配方判法的內部,沒有碰到它們的程式路徑,答「不受影響」。

## F1 `--json` 的替身字元跳脫只在最後印出時做,寫 kill-log 那一步先當掉;invariant、test、platform、note、covers 帶替身字元時 `--json` 照樣當掉,Issue 卻寫成「只有人讀輸出會崩」
severity: minor
blocking: 否
引句:「輸出遇到落單替身字元改寫成 JSON 跳脫、不再崩」
file: `scripts/lumos:15283`(寫 kill-log:`fh.write(json.dumps({...}, ensure_ascii=False) + "\n")`,檔案用 UTF-8 開,替身字元在這裡丟 UnicodeEncodeError)
file: `scripts/lumos:15296`(替身字元的改寫只在這一行,也就是 kill-log 寫完之後才印 `--json` 的地方)

1. **發生什麼:** 改寫只包住最後印 `--json` 的那一行。可是在那之前,留痕會把 invariant、test、platform、note、tail、covers 用 `ensure_ascii=False` 寫進 UTF-8 檔,只要這幾個欄位帶落單替身字元,就先在寫檔時當掉。結果只有 old、detail、attr_excerpt 這幾個不寫進 kill-log 的欄位真的修好了。
2. **最小重現**(`repro_json.py`,每列一個新 repo,配方只改一個欄位,跑 `guard kill Systems/Limit --json`):
   ```
   == good: rc=1 stdout行數=1 JSON ok, verdict=['killed_unattributed'], 原文中文=True
   == old 帶替身: rc=2 stdout行數=1 JSON ok, verdict=['drifted'], 原文中文=True
   == invariant 帶替身: rc=1 stdout行數=0 非 JSON ["UnicodeEncodeError: 'utf-8' codec can't encode character '\\ud800' in position 98: surrogates not allowed"] ['fh.write(json.dumps({"ts": ts, "node": rel, "commit": commit,']
   == note 帶替身: rc=1 stdout行數=0 非 JSON [UnicodeEncodeError ...] ['fh.write(...']
   == test 帶替身: rc=1 stdout行數=0 非 JSON [UnicodeEncodeError ...] ['fh.write(...']
   == covers 帶替身: rc=1 stdout行數=0 非 JSON [UnicodeEncodeError ...] ['fh.write(...']
   == detail 帶替身: rc=1 stdout行數=1 JSON ok
   ```
   網格的結果一致:`inv=替身`、`plat=替身`、`file=替身` 在 `--json` 模式下帶不帶 `--id` 都是 `1💥`,`test=替身` 不帶 `--id` 時也是。對照組 573d911e 一樣會崩,所以這不是這段修正造成的回歸。
3. **跟筆記對不上(這是要改的地方):**
   - Issue 的 WHY 行說「`--json` 輸出遇到落單替身字元改寫成 JSON 跳脫、不再崩」,又把仍會崩的寫成「invariant/platform/file/test 帶替身字元時的**人讀輸出**」;帶 `--id` 的那份也寫「人讀輸出仍會崩」。實測 `--json` 對這四種一樣會崩。
   - note、covers 帶替身字元的情形兩份清單都沒列。
   - 計劃〈實作紀錄〉寫「`--json` 遇到替身字元崩 → 改寫成 JSON 跳脫」,也沒交代只修了部分欄位。

   下一個 session 讀到會以為 `--json` 已經安全。
4. **為什麼只標 minor:** 這類配方只有手改筆記才會出現,kill-add 寫不出來;當掉是既有行為,這段修正也沒有讓它變得更糟。依抑噪紀律,不是新增的錯誤行為,所以不升 major。
5. **建議(擇一):**
   - 寫 kill-log 那一行也用同一個改寫,把替身字元寫成 `\uXXXX` 跳脫。最好抽成一支 `_json_line_surrogate_safe(obj)`,讓 kill-log 和 `--json` 輸出共用,同一個判斷只寫一次。改完後,`--json` 對這幾種就真的不會崩,只剩人讀輸出會崩。
   - 不改程式,就把 Issue 的兩份清單改成「人讀和 `--json` 都會崩」並補上 note、covers,〈實作紀錄〉也補一句「只修了不寫進 kill-log 的欄位」。

   如果選改程式,`t_guard_kill_only_ids` 加一格「invariant 帶替身字元加 `--json`」先紅再修。

最高等級:minor,blocking 共 0 條
