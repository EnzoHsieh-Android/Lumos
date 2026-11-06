severity: minor

## F1 路徑文字含佔位符字樣時,替換雖然只換一次,但執行入口會因為成品裡還有那串字而拒跑,閘轉成環境問題自動放行
severity: minor
blocking: 否
引句:「★兩個佔位符在一次掃描裡換完★:連續兩次字串替換的話,第二次會重掃第一次換進去的路徑(路徑裡剛好有佔位符字樣就被再換一次)。」
file: `scripts/lumos:39602`(`_lint_run_and_parse` 的 `if _lint_gate_covers(cmd): return [], False`,對象是已經換好檔名的成品命令)
file: `scripts/lumos:40594`(`_lint_new_run_one` 把 `ok=False` 且沒有 `too_long` 的情況記成 `"env"`)

走一遍:
1. 改動檔是 `x{LINT_FILES}.kt` 和 `b.kt`,宣告命令含 `{LINT_FILES_CSV}`。
2. `_lint_cmd_with_files` 單次掃描,換出 `true 'x{LINT_FILES}.kt,b.kt'; ...`。這一步正確。
3. 這個成品命令傳進 `_lint_run_and_parse`,第一道檢查 `_lint_gate_covers(cmd)` 看到成品裡還有 `{LINT_FILES}` 字樣,回 `([], False)`。
4. `_lint_new_run_one` 因為沒有 `too_long`,回 `(None, "env")`。
5. `_lint_new_run_cmds` 把它記成 `undone` 的 `env`,`_lint_new_classify` 走自動放行。一條「該檢查卻沒檢查」的命令被當成環境不可用放行。

這個行為在改動前就有(舊碼是 `_LINT_NEW_FILES_TOKEN in cmd`),這次沒有新引入。但 diff 的註解和計劃 S1 都宣稱「路徑裡有佔位符字樣也不會被再換」,端到端並沒有做到。逗號佔位符的 `{LINT_FILES_CSV}` 字樣也一樣會觸發。威脅模型是單人加 AI 依序操作,不防刻意偽造,所以只給 minor。

重現(`python3.14 -I`,把 lumos 當模組載入,命令是 `true {LINT_FILES_CSV}; echo '<最小 SARIF>' > {LINT_SARIF_OUT}`):
```
['a.kt','b.kt']              -> ([], True)
['x{LINT_FILES}.kt','b.kt']  -> ([], False)   # 命令其實跑得動
['x{LINT_FILES_CSV}.kt']     -> ([], False)
```
重現檔是臨時目錄裡的腳本,我已刪掉。

## F2 計劃本文的 S7 與 REVISIT 還寫 T3,程式與提醒文字用的是 T4
severity: minor
blocking: 否
引句:「T4 是 [[Projects/Android的detekt推送前真的擋_計劃]] 範圍 5 新增的那則(計劃字面叫 T3,但 T3 已是「等號寫法」,改用 T4)」
file: `docs/lumos-toolchain-knowledge/Projects/Android的detekt推送前真的擋_計劃.md:85`、`:99`

diff 裡 `_DETEKT_ADVICE_ORDER` 和提醒文字都是 T4。計劃第 85 行驗收條款寫「應 印 T3」,第 99 行 REVISIT 寫「T3 的字樣比對」。照條款去寫測試或對照的人會去找一個已經是「等號寫法」的 T3,兩邊對不上。測試和文件另有人審,這條只提醒對不上。

## 其他鏡頭的結論(走過,沒有 finding)
- **100,000 位元組邊界**:`_lint_csv_batches` 用 `<=`。我造了一條剛好 99,998 位元組的命令,沒被切開。5,000 支檔切成 4 批,每批 71 KB 到 72 KB,總檔數 5,000,沒少沒重。
- **單檔超長**:只剩一支時照送。`_lint_spawn` 接 E2BIG,`_lint_run_and_parse` 的 `finally` 會 `os.unlink` 暫存 SARIF,錯誤路徑也收得掉。
- **兩種佔位符同一條命令**:單次 `re.sub` 加 lambda,不會被替換字串裡的反斜線影響。
- **分批後的告警**:各批檔案不重疊,不會重複或少算。任一批失敗就整條丟棄,不留半份。
- **分隔字元路徑**:`_lint_new_sep_split` 用現在路徑判斷。改名修掉逗號的情形(舊名有逗號、新名沒有),檔案以新名為鍵,不會誤擋。
- **`_lint_gate_covers` 的 kind**:各呼叫點(P2 傳 `list`、冒煙過濾和 `_lint_new_run_one` 傳 `csv`)都對。
- **只准一處替換**:新程式沒有在 `_lint_cmd_with_files` 外自己做替換。`_lint_csv_quoted_alone` 只做字面判斷,已列進 `t_lint_files_substitution_has_one_implementation` 的白名單。
- **CI 步驟**:`set -eu` 加 `sha256sum -c -`,雜湊不符會讓整步失敗;沒有快取,所以每次都會比對。

## 圖譜鏡頭逐篇判定
(`lumos contracts` 對這四篇都回「沒有登記任何合約」,所以沒有 ★INVARIANT★ 可破。)
- **Systems/pitfalls-lint-adapter**:不影響。新增的 WHY 行寫「辨認兩種佔位符全走 `_lint_gate_covers`」,與 diff 一致;舊 `{LINT_FILES}` 的替換語意沒變。
- **Systems/pitfalls-code-loop**:不影響其他規則。新增的 WHY 行(分隔字元路徑、分批、參數太長擋下)與 diff 一致。F1 是這條 WHY 沒涵蓋的邊角,未破壞任何 PITFALL。
- **Systems/lint-declaration-health**:不影響。WHY 行與 diff 一致:T4 取代 T3、P2 只看舊佔位符、引號單獨包住記成格式問題。它也自己寫明「計劃字面叫 T3」,與 F2 同源。
- **Projects/Android的detekt規則說實話_計劃**:不影響。判定表 P1、P2、T4 的文字與程式吻合,並且已經註明 T3 改 T4。

## manifest 判定
沒拿到 pitfalls manifest。這個 repo 判定併發類題目屬範圍外,本案沒有相關項。

severity: minor
