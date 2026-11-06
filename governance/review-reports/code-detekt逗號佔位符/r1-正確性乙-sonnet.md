severity: minor

整份「測試與文件」包的行為宣稱我都核對過,測試抓得住錯。只有一處文件內部不一致(F1,minor)。我在 `/tmp/lumos-seat-work/code-detekt逗號佔位符/正確性乙-sonnet/r` 做了臨時複本。S1–S8 共 6 組關鍵字(22、22、6、2、14、6 個通過)全綠,本機有 detekt 1.23.8,S8 真跑過。

## F1 計劃的驗收條款 S7、天花板、REVISIT 仍寫 T3,實作、測試、其他筆記都用 T4
severity: minor
blocking: 否
引句:「計劃寫 T3,但 T3 這個代號已經是「等號寫法」,新的這則用 T4」
file: `docs/lumos-toolchain-knowledge/Projects/Android的detekt推送前真的擋_計劃.md:85`
file: `scripts/lumos:38798`

1. 這個 diff 把程式(`_DETEKT_ADVICE_ORDER` 含 T4)、測試(`t_lint_detekt_advice_csv_and_ci` 斷言 `T4:`)、`lint-declaration-health`、規則說實話計劃的判定表都改成 T4。
2. 但綁這支測試的計劃本身沒改。第 85 行 S7 寫「應 印 T3」,第 96 行天花板寫「(T3)」,第 99 行 REVISIT 寫「同步改範本與 T3 的字樣比對」,第 100 行 REVISIT 寫「把 T3 升級成問題」。
3. 在程式裡 T3 是「等號寫法」那則(`scripts/lumos:38798`)。照第 99、100 行回頭做的人會去改錯那一則。
4. 「T3 被佔用、改叫 T4」只寫在規則說實話計劃、`lint-declaration-health` 的 WHY 和測試 docstring。驗收條款是已凍結的,所以不能直接改。
5. 這是代號不一致,不是行為錯。建議在計劃加一行更正括號,或在兩條 REVISIT 旁註明是 T4。

## 測試品質:逐條核對與改壞驗證

我把程式改壞後各跑一次對應測試,6 種改壞都有翻紅。其中 M3 的失敗訊息證明測試真的在驗「參數太長不是環境放行」,不是被別的守衛代打。

| 改壞 | 對應測試 | 結果 |
|---|---|---|
| M1 分批後丟掉最後一批 | `t_lint_new_csv_batches` | 紅:「每一邊每支檔都剛好跑到一次」和「合併後結果相同」都失敗,少了 F11 那條 |
| M2 分隔字元只判逗號、不判分號 | `t_lint_new_csv_separator_path` | 紅:5 條斷言失敗 |
| M3 參數太長被記成 env | `t_lint_new_csv_batches` | 紅:實際變成 `env-unavailable` 自動放行 |
| M4 只有現在版分批、改動前版不分批 | `t_lint_new_csv_batches` | 紅:「每一批換完的命令都在上限內」失敗 |
| M5 分隔字元把全部檔拿光時仍判乾淨 | `t_lint_new_csv_separator_path` | 紅:實際判成 `clean` |
| M6 替換時不轉相對路徑 | `t_lint_new_csv_separator_path` | 紅:收到絕對路徑 |

- **判準獨立性**:S1 的預期值是手寫字串,再加 `shlex.split` 還原確認,不是用被測函式算 expected。S4 的對照組(舊 `{LINT_FILES}` 讓假 detekt 拒跑)反映真實行為。
- **假 detekt 形狀**:規則名、level、訊息、`startLine` 等欄位和我跑真 detekt 的 SARIF 一致。`artifactLocation.uri` 不同,真的會百分比編碼,假的是原樣加 `file://`。測試路徑全是 ASCII 且沒有空白,所以不影響結果,也講不出會因此誤判的輸入。
- **S8 沒裝 detekt 時**:本機版本不是 1.23.8 就印略過,但先驗過共用設定檔存在;只有 `CI` 環境變數存在時才判紅,符合 S8 條款「本機略過、CI 一定有」。`.github/workflows/ci.yml:150` 有釘版本並比對 sha256 的安裝步驟,所以不是假綠。
- **S5 參數太長**:測試用 3 MB 命令真的觸發 E2BIG,macOS 和 Linux 都成立。
- **`t_lint_files_substitution_has_one_implementation`**:白名單從 4 支改成 3 支,拿掉了執行入口、冒煙、規則索引三處,守衛比原本更緊。

## 文件正確性

- **旗標、任務名、佔位符**:`linter精選目錄` 的 lint.json 樣板、CI 範本(`detektBaseline<變體>`、`detekt<變體>`、純 Kotlin 模組用 `detektMain`)、`android.yml` 註解和 kotlin-idioms 的說法彼此一致,也和程式行為一致。S9(在 Gradle 專案實跑)是人工驗收,沒有執行。
- **筆記對得上程式**:筆記裡所有 `[test:…]` 名稱在 `scripts/test_lumos.py` 都找得到。`_lint_gate_covers`、`_lint_csv_quoted_alone`、`_lint_sep_path`、`_lint_csv_batches`、`fail_info` 都在 `scripts/lumos` 裡,行為也和筆記描述相符。
- **冒煙「取前三支」**:程式的 `sample=3` 與筆記一致。
- **健檢也記成格式問題**:筆記說健檢 F 段會把「引號單獨包住佔位符」列成宣告問題,這成立,因為健檢和 lint-check 共用 `_lint_load_and_validate`。
- **摘要行前綴**:新增的都是 WHY,帶 `[出處:]` 和 `[因:]`;沒有新增 RULE 或 FACT。

## 圖譜鏡頭逐篇判定

- **Systems/pitfalls-lint-adapter**:不影響。這篇沒有 ★INVARIANT★、RULE:、PITFALL: 行。原本「detekt 多檔拒跑、推送時放行」那句已被改成指向逗號佔位符一節。新行為(替換只有一處、辨認只有一處)也和第 130 行「冒煙取前三支」不衝突。
- **Systems/pitfalls-code-loop**:不影響。既有的 PITFALL: 和 RULE:(第 39–41、59–61、72、81 行)講的是代碼審記帳、資安席範圍、判定檔,和這次改動無關。第 211–212 行「檔太大不走自動放行、登記後照列」的原則,新增的分隔字元路徑與參數太長都照同一規則處理,沒有矛盾。
- **Systems/lint-declaration-health**:不影響。這篇沒有合約行。新增的「引號單獨包住佔位符」格式校驗是在原本三項校驗上多一項。原有 WHY 說「提醒只提醒不改退出碼」,T4 同樣遵守。
- **Systems/linter精選目錄**:不影響。這篇沒有 ★INVARIANT★、RULE:,只有第 272 行屬架構 lint 的 ★INVARIANT★。FACT 行(只給 `--input` 時型別規則不報)有 `[來源:]` 和 `[confirmed:]`,在這次新行為下仍然成立。被移除的「推送時不擋」REVISIT 已被正文取代。
- **Projects/Android的detekt規則說實話_計劃**:不影響。這篇沒有 ★INVARIANT★、RULE:、PITFALL: 行。判定表的 T1、P1、P2 和新增的 T4 與 `_DETEKT_ADVICE_TEXT` 一致。唯一問題是 F1 的代號說明沒有回到「推送前真的擋」計劃本身。

## 備註

- 我的臨時目錄 `/tmp/lumos-seat-work/code-detekt逗號佔位符/正確性乙-sonnet/` 還在,內含複本 `r/`、改壞腳本 `mut.py`、`lumos.orig`、`d/`。按派工規定由編排者收貨後刪。複本的 `scripts/lumos` 已還原成原樣。
- 原 repo 的 `git status` 有 `docs/.governance-log.jsonl` 已修改、`governance/review-reports/code-detekt逗號佔位符/` 未追蹤,不是我造成的,我沒碰。

severity: minor
